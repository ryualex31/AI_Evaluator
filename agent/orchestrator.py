from agent.guardrails import classify_intent
from agent.tools import generate_sql, execute_sql
from agent.prompts import (
    fix_sql_prompt,
    insight_prompt,
    answer_prompt,
    direct_answer_prompt,
    sql_prompt
)
from agent.evaluator import evaluate_response
from utils.llm import call_llm
from utils.formatter import to_markdown_table
from utils.logger import log_interaction

MAX_RETRIES = 2


def run_agent(user_query, schema):

    # ---------------- INTENT ---------------- #
    intent = classify_intent(user_query)

    # ---------------- SAFE NON-FINANCE HANDLING ---------------- #
    if intent == "GREETING":
        response = "Hi! I’m your AI Financial Analyst. You can ask me about revenue, profit, trends, and business performance."
        log_interaction({
            "query": user_query,
            "intent": intent,
            "response": response
        })
        return {"message": response}

    if intent == "GENERAL_QUERY":
        response = "I’m an AI Financial Analyst. I can help you analyze revenue, profit, trends, and business performance. Try asking something like 'Total revenue by region'."
        log_interaction({
            "query": user_query,
            "intent": intent,
            "response": response
        })
        return {"message": response}

    if intent == "IRRELEVANT_QUERY":
        response = "Sorry, I can only assist with finance-related queries such as revenue, profit, and business performance."
        log_interaction({
            "query": user_query,
            "intent": intent,
            "response": response
        })
        return {"message": response}

    # ---------------- SQL GENERATION ---------------- #
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

        return {
            "error": "Unable to process request. Please refine your query."
        }

    columns, rows = result
    preview_rows = rows[:10]

    # ---------------- DIRECT ANSWER ---------------- #
    direct_answer = call_llm(
        direct_answer_prompt(user_query, preview_rows)
    )

    # ---------------- SECONDARY ANSWER ---------------- #
    answer = call_llm(
        answer_prompt(user_query, preview_rows)
    )

    # ---------------- TABLE ---------------- #
    table_md = to_markdown_table(columns, rows)

    # ---------------- SIMPLE VS ANALYTICAL ---------------- #
    simple_keywords = ["top", "highest", "total", "sum", "list"]
    is_simple = any(word in user_query.lower() for word in simple_keywords)

    # ---------------- INSIGHT ---------------- #
    insight = None
    insight_prompt_used = None

    if not is_simple:
        insight_prompt_used = insight_prompt(user_query, preview_rows)
        insight = call_llm(insight_prompt_used)

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
        "direct_answer": direct_answer,
        "answer": answer,
        "insight_prompt": insight_prompt_used,
        "insight": insight,
        "evaluation": evaluation,
        "retries": retries
    })

    # ---------------- FINAL RESPONSE ---------------- #
    return {
        "direct_answer": direct_answer,
        "answer": answer,
        "table": table_md,
        "insight": insight,
        "evaluation": evaluation,
        "columns": columns,
        "rows": rows,
        "retries": retries
    }