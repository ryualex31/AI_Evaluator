from agent.guardrails import classify_intent
from agent.tools import generate_sql, execute_sql
from agent.prompts import (
    fix_sql_prompt,
    insight_prompt,
    summary_prompt, 
    sql_prompt,
    non_finance_prompt,
    chart_prompt
)
from agent.evaluator import evaluate_response
from utils.llm import call_llm
from utils.formatter import to_markdown_table
from utils.logger import log_interaction

import json

MAX_RETRIES = 2


def run_agent(user_query, schema):

    # ---------------- INTENT ---------------- #
    intent = classify_intent(user_query)

    # ---------------- NON-FINANCE ---------------- #
    if intent != "FINANCE_QUERY":
        try:
            response = call_llm(non_finance_prompt(user_query))
        except Exception:
            response = (
                "I'm here to help with financial insights like revenue, "
                "profit, and business trends."
            )

        log_interaction({
            "query": user_query,
            "intent": intent,
            "response": response
        })

        return {"message": response}

    # ---------------- SQL ---------------- #
    retries = 0
    sql_query = None
    result = None
    sql_prompt_used = sql_prompt(user_query, schema)

    while retries <= MAX_RETRIES:

        if retries == 0:
            sql_query = generate_sql(user_query, schema)
        else:
            fix_prompt = fix_sql_prompt(user_query, sql_query, result, schema)
            sql_query = call_llm(fix_prompt).strip()

        result = execute_sql(sql_query)

        if isinstance(result, tuple):
            break

        retries += 1

    # ---------------- FAILURE ---------------- #
    if not isinstance(result, tuple):

        log_interaction({
            "query": user_query,
            "intent": intent,
            "sql_query": sql_query,
            "error": result,
            "retries": retries
        })

        return {"error": "Unable to process request. Please refine your query."}

    columns, rows = result
    preview_rows = rows[:10]

    # ---------------- SUMMARY (REPLACES ANSWER) ---------------- #
    summary = call_llm(
        summary_prompt(user_query, preview_rows)
    )

    # ---------------- TABLE ---------------- #
    table_md = to_markdown_table(columns, rows)

    # ---------------- INSIGHT ---------------- #
    simple_keywords = ["top", "highest", "total", "sum", "list"]
    is_simple = any(word in user_query.lower() for word in simple_keywords)

    insight = None
    insight_prompt_used = None

    if not is_simple:
        insight_prompt_used = insight_prompt(user_query, preview_rows)
        insight = call_llm(insight_prompt_used)

    # ---------------- CHART ---------------- #
    chart = None
    chart_prompt_used = None

    try:
        chart_prompt_used = chart_prompt(user_query, columns, preview_rows)
        chart_response = call_llm(chart_prompt_used).strip()

        if chart_response.upper() != "NONE":

            # Clean markdown
            if "```" in chart_response:
                parts = chart_response.split("```")
                chart_response = parts[1] if len(parts) > 1 else parts[0]

            chart = json.loads(chart_response)

            valid_types = ["line", "bar", "area", "pie"]

            if isinstance(chart, dict) and chart.get("type") in valid_types:

                # Normalize columns
                columns_lower = [c.lower() for c in columns]

                x = chart.get("x", "").lower()
                y = chart.get("y", "").lower()

                # Alias handling
                alias_map = {
                    "profit": "total_profit",
                    "revenue": "total_revenue"
                }

                if y not in columns_lower and y in alias_map:
                    y = alias_map[y]

                if x in columns_lower and y in columns_lower:
                    chart["x"] = columns[columns_lower.index(x)]
                    chart["y"] = columns[columns_lower.index(y)]
                else:
                    chart = None
            else:
                chart = None

    except Exception:
        chart = None

    # ---------------- FALLBACK CHART ---------------- #
    if chart is None and len(rows) > 1 and len(columns) >= 2:
        chart = {
            "type": "bar",
            "x": columns[0],
            "y": columns[1],
            "reason": "Fallback comparison chart"
        }

    # ---------------- EVALUATION ---------------- #
    evaluation = evaluate_response(
        user_query,
        sql_query,
        preview_rows,
        insight
    )

    # ---------------- LOGGING ---------------- #
    log_interaction({
        "query": user_query,
        "intent": intent,
        "sql_prompt": sql_prompt_used,
        "sql_query": sql_query,
        "columns": columns,
        "rows_preview": preview_rows,
        "summary": summary,
        "insight_prompt": insight_prompt_used,
        "insight": insight,
        "chart_prompt": chart_prompt_used,
        "chart": chart,
        "evaluation": evaluation,
        "retries": retries
    })

    # ---------------- FINAL ---------------- #
    return {
        "summary": summary,
        "table": table_md,
        "insight": insight,
        "evaluation": evaluation,
        "columns": columns,
        "rows": rows,
        "chart": chart,
        "retries": retries
    }