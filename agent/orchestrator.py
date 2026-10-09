import json
import logging
import re

from agent.guardrails import classify_intent
from agent.tools import generate_sql, execute_sql
from agent.prompts import fix_sql_prompt, insight_prompt, summary_prompt, non_finance_prompt, chart_prompt, sql_prompt
from agent.evaluator import evaluate_response
from utils.llm import call_llm
from utils.formatter import to_markdown_table
from utils.logger import log_interaction
from utils.presentation import default_chart, normalize_chart

MAX_RETRIES = 2


def _log(data):
    try:
        log_interaction(data)
    except Exception:
        logging.warning("Interaction logging is unavailable.")


def run_agent(user_query, schema, user_email=None):
    try:
        return _run_agent(user_query, schema, user_email)
    except Exception:
        logging.warning("Analysis provider request failed.")
        _log({"user_email": user_email, "query": user_query, "error": "Analysis provider request failed."})
        return {"error": "The analysis service is unavailable. Please try again."}


def _run_agent(user_query, schema, user_email):
    intent = classify_intent(user_query)
    if intent != "FINANCE_QUERY":
        response = call_llm(non_finance_prompt(user_query))
        _log({"user_email": user_email, "query": user_query, "intent": intent, "response": response})
        return {"message": response}

    sql_query, result = None, None
    sql_prompt_used = sql_prompt(user_query, schema)
    for retries in range(MAX_RETRIES + 1):
        if retries == 0:
            sql_query = generate_sql(user_query, schema)
        else:
            sql_query = call_llm(fix_sql_prompt(user_query, sql_query, result, schema)).strip()
            sql_query = re.sub(r"^```(?:sql)?\s*|\s*```$", "", sql_query)
        result = execute_sql(sql_query)
        if isinstance(result, tuple):
            break
    else:
        _log({"user_email": user_email, "query": user_query, "intent": intent,
              "sql_query": sql_query, "sql_prompt": sql_prompt_used, "error": result, "retries": retries})
        return {"error": "Unable to process this query. Try a narrower date range or simpler grouping."}

    columns, rows = result
    # execute_sql rejects oversized results; these are complete, never a sample.
    data = {"columns": columns, "rows": rows}
    if not rows:
        _log({"user_email": user_email, "query": user_query, "intent": intent,
              "sql_query": sql_query, "summary": "No matching data was found.", "rows_preview": [], "retries": retries})
        return {"summary": "No matching data was found.", "columns": columns, "rows": rows, "sql_query": sql_query}
    summary = call_llm(summary_prompt(user_query, data))
    simple = any(word in user_query.lower() for word in ("top", "highest", "total", "sum", "list"))
    insight = None
    insight_prompt_used = None
    if not simple:
        try:
            insight_prompt_used = insight_prompt(user_query, data)
            insight = call_llm(insight_prompt_used)
        except Exception:
            pass

    chart = default_chart(columns, rows)
    chart_prompt_used = None
    if chart:
        try:
            chart_prompt_used = chart_prompt(user_query, columns, rows)
            response = call_llm(chart_prompt_used).strip()
            response = re.sub(r"^```(?:json)?\s*|\s*```$", "", response)
            chart = normalize_chart(json.loads(response), columns, rows) or chart
        except Exception:
            pass

    evaluation = evaluate_response(user_query, sql_query, data, insight, summary=summary)
    _log({"user_email": user_email, "query": user_query, "intent": intent,
          "sql_query": sql_query, "columns": columns, "rows_preview": rows[:10],
          "summary": summary, "insight": insight, "chart": chart,
          "sql_prompt": sql_prompt_used, "insight_prompt": insight_prompt_used, "chart_prompt": chart_prompt_used,
          "evaluation": evaluation, "retries": retries})
    return {"summary": summary, "table": to_markdown_table(columns, rows), "insight": insight,
            "evaluation": evaluation, "columns": columns, "rows": rows,
            "chart": chart, "sql_query": sql_query, "retries": retries}
