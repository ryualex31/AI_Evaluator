from agent.guardrails import classify_intent
from agent.tools import generate_sql, execute_sql
from agent.prompts import insight_prompt
from utils.llm import call_llm

MAX_RETRIES = 2


def fix_sql_prompt(user_query, failed_sql, error, schema):
    return f"""
You are an expert SQL debugger.

The following SQL query failed:

SQL Query:
{failed_sql}

Error:
{error}

Database Schema:
{schema}

Fix the SQL query.

Rules:
- Use ONLY the given schema
- Do NOT hallucinate columns
- Do NOT use joins
- Return ONLY the corrected SQL query

Original Question:
{user_query}
"""


def run_agent(user_query, schema):

    # 🔹 Step 1: Intent Classification
    intent = classify_intent(user_query)

    # 🟡 GENERAL queries
    if intent == "GENERAL_QUERY":
        return {
            "message": (
                "Hi! I’m your AI Financial Analyst 📊\n\n"
                "I can help you analyze financial data such as:\n"
                "- Revenue trends\n"
                "- Profit analysis\n"
                "- Top-performing regions or products\n\n"
                "Try asking something like:\n"
                "'Total revenue by region'"
            )
        }

    # 🔴 IRRELEVANT queries
    if intent == "IRRELEVANT_QUERY":
        return {
            "message": (
                "I’m here to help with financial analysis 📊\n\n"
                "Please ask questions related to revenue, profit, or business performance."
            )
        }

    # 🟢 FINANCE queries → continue pipeline
    retries = 0
    sql_query = None
    result = None

    while retries <= MAX_RETRIES:

        if retries == 0:
            sql_query = generate_sql(user_query, schema)
        else:
            prompt = fix_sql_prompt(user_query, sql_query, result, schema)
            sql_query = call_llm(prompt).strip()

        result = execute_sql(sql_query)

        # Success case
        if isinstance(result, tuple):
            break

        retries += 1

    # Failure after retries
    if not isinstance(result, tuple):
        return {
            "error": (
                "I couldn’t process that query. Try rephrasing your question "
                "to be more specific about the financial data you need."
            )
        }

    columns, rows = result

    # Limit rows for insight generation
    preview_rows = rows[:10]

    insight = call_llm(
        insight_prompt(user_query, preview_rows)
    )

    return {
        "columns": columns,
        "rows": rows,
        "insight": insight,
        "retries": retries
    }