def generate_sql_prompt(user_query, schema):
    return f"""
You are an expert data analyst.

Your task is to convert natural language questions into SQL queries.

DATABASE SCHEMA:
{schema}

RULES:
- Use ONLY the table 'financials'
- Do NOT hallucinate columns
- Do NOT use joins
- Return ONLY SQL query
- Use aggregation when needed
- Use GROUP BY appropriately

EXAMPLES:

Q: Total revenue by region
SQL:
SELECT region, SUM(revenue) as total_revenue
FROM financials
GROUP BY region;

Q: Top 3 products by profit
SQL:
SELECT product, SUM(profit) as total_profit
FROM financials
GROUP BY product
ORDER BY total_profit DESC
LIMIT 3;

---

Q: {user_query}
SQL:
"""


def insight_prompt(user_query, data):
    return f"""
You are a senior financial analyst.

User Question:
{user_query}

Data:
{data}

Provide:
- Key insight
- Trends or observations
- Keep it concise and business-friendly

Do NOT mention SQL.
"""
