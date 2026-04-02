# ---------------- INTENT CLASSIFIER ---------------- #
def intent_prompt(query):
    return f"""
You are an intelligent query classifier for a financial AI assistant.

Classify the user query into ONE of the following:

1. FINANCE_QUERY → financial analysis, revenue, cost, profit, trends
2. GENERAL_QUERY → "who are you", "what can you do"
3. GREETING → greetings like "hi", "hello", "hey"
4. IRRELEVANT_QUERY → jokes, unrelated topics

Query:
"{query}"

Return ONLY one label.
"""


# ---------------- SQL GENERATION ---------------- #
def sql_prompt(query, schema):
    return f"""
You are an expert SQL generator for a financial analytics system.

Your task:
Convert the user question into a valid SQLite SQL query.

DATABASE SCHEMA:
{schema}

AVAILABLE COLUMNS:
- date, month, year
- region, country
- product, category
- customer_type, supplier
- revenue, cost, profit, profit_margin
- units_sold, discount

STRICT RULES:
1. Use ONLY the given schema
2. DO NOT hallucinate columns
3. DO NOT use JOINs
4. Use GROUP BY for aggregations
5. Use ORDER BY for ranking (e.g., "top", "highest")
6. Use LIMIT when needed
7. Keep SQL simple and valid for SQLite

OUTPUT:
Return ONLY the SQL query (no explanation, no markdown)

USER QUESTION:
{query}
"""


# ---------------- SQL FIX ---------------- #
def fix_sql_prompt(query, failed_sql, error, schema):
    return f"""
You are an expert SQL debugger.

The following SQL query failed.

FAILED SQL:
{failed_sql}

ERROR:
{error}

DATABASE SCHEMA:
{schema}

INSTRUCTIONS:
- Fix the SQL query
- Use ONLY the schema
- DO NOT hallucinate columns
- DO NOT use JOINs
- Keep it valid SQLite

Return ONLY the corrected SQL.

USER QUESTION:
{query}
"""


# ---------------- INSIGHT GENERATION ---------------- #
def insight_prompt(query, data):
    return f"""
You are a senior financial analyst.

Analyze the data and provide:

1. Key Insight
2. Business Interpretation
3. Recommendation

Keep it concise and business-focused.

DATA:
{data}

QUESTION:
{query}
"""


# ---------------- CONVERSATIONAL HANDLING ---------------- #
def conversational_prompt(query, intent):
    return f"""
You are a friendly AI Financial Analyst assistant.

User query:
"{query}"

Intent: {intent}

Behavior:

IF GREETING:
- Greet warmly
- Introduce yourself
- Suggest example questions

IF GENERAL_QUERY:
- Explain what you can do
- Give examples

IF IRRELEVANT_QUERY:
- Politely decline
- Redirect to finance queries

Guidelines:
- Be natural
- Be concise
- Do NOT mention intent labels

Respond directly.
"""

def summary_prompt(query, data):
    return f"""
You are a financial analyst writing a business summary.

Your task is to summarize the results based ONLY on the data.

STRICT GUIDELINES:

1. Be factual and precise
2. DO NOT use vague terms like:
   - "very high", "very low", "huge", "massive"
3. ONLY make comparisons if multiple data points exist
4. If no comparison is possible → just state the result
5. Use neutral, professional financial language
6. Keep it concise (2–3 sentences max)

GOOD EXAMPLES:
- "North America generated the highest revenue among regions."
- "Cloud Infrastructure contributes the largest share of total revenue."

BAD EXAMPLES:
- "Revenue is very high"
- "This is performing extremely well"

DATA:
{data}

QUESTION:
{query}
"""

def evaluation_prompt(query, sql, data, insight):
    return f"""
You are an expert evaluator of financial AI systems.

Evaluate the response based on the following:

USER QUESTION:
{query}

SQL GENERATED:
{sql}

DATA RETURNED:
{data}

INSIGHT:
{insight}

METRICS:

1. Accuracy (0-10)
- Does the insight correctly reflect the data?
- Any incorrect statements?

2. Coverage (0-10)
- Does it fully answer the question?
- Or partially?

3. Faithfulness (0-10)
- Is the insight grounded strictly in the data?
- Any hallucinations or assumptions?

4. Clarity (0-10)
- Is it easy to understand?
- Well structured?

OUTPUT FORMAT (STRICT):

Accuracy: X/10  
Coverage: X/10  
Faithfulness: X/10  
Clarity: X/10  
Overall: X/10  

Reason:
<concise justification>
"""# ---------------- INTENT ---------------- #
def intent_prompt(query):
    return f"""
Classify into ONE:
- FINANCE_QUERY
- GENERAL_QUERY
- GREETING
- IRRELEVANT_QUERY

Query:
"{query}"

Return ONLY label.
"""


# ---------------- SQL ---------------- #
def sql_prompt(query, schema):
    return f"""
Generate SQLite SQL.

SCHEMA:
{schema}

RULES:
- Use ONLY schema
- No JOINs
- Use SUM/GROUP BY for aggregations
- Use ORDER BY + LIMIT for ranking

Return ONLY SQL.

QUESTION:
{query}
"""


# ---------------- SQL FIX ---------------- #
def fix_sql_prompt(query, failed_sql, error, schema):
    return f"""
Fix SQL.

FAILED:
{failed_sql}

ERROR:
{error}

SCHEMA:
{schema}

Return ONLY corrected SQL.

QUESTION:
{query}
"""


# ---------------- ANSWER ---------------- #
def answer_prompt(query, data):
    return f"""
You are a financial analyst.

Provide a DIRECT answer.

RULES:
- 1–2 sentences
- No fluff
- No vague terms
- No bullets

DATA:
{data}

QUESTION:
{query}
"""


# ---------------- INSIGHT ---------------- #
def insight_prompt(query, data):
    return f"""
Provide short business insights ONLY if needed.

RULES:
- 2-3 insights based on data
- use bullets for each insight
- No fluff
- do not repeat the direct answer
- if there's no insight - do no add anything beyond the direct answer

DATA:
{data}

QUESTION:
{query}
"""


# ---------------- CONVERSATIONAL ---------------- #
def conversational_prompt(query, intent):
    return f"""
You are a friendly AI Financial Analyst.

User:
"{query}"

Intent: {intent}

Handle appropriately:
- GREETING → greet + examples
- GENERAL → explain capabilities
- IRRELEVANT → redirect

Keep concise.
"""


# ---------------- EVALUATION ---------------- #
def evaluation_prompt(query, sql, data, insight):
    return f"""
Evaluate response.

QUESTION:
{query}

SQL:
{sql}

DATA:
{data}

INSIGHT:
{insight}

Return STRICT JSON:

{{
  "accuracy": 0-10,
  "coverage": 0-10,
  "faithfulness": 0-10,
  "clarity": 0-10,
  "overall": 0-10,
  "reason": "short explanation"
}}
"""


def direct_answer_prompt(query, data):
    return f"""
You are a financial analyst.

Answer the question in a natural, conversational way.

RULES:
- Frame the response using the question context
- 1 sentence only
- Be precise and factual
- Include key value(s)
- No bullet points
- No fluff

EXAMPLES:
Q: What is total revenue in 2024?
A: The total revenue in 2024 is 1.2M.

Q: Which product has highest profit?
A: Cloud Infrastructure has the highest profit.

DATA:
{data}

QUESTION:
{query}
"""

def non_finance_prompt(query):
    return f"""
You are an AI Financial Analyst assistant.

The user asked something unrelated to finance:

"{query}"

Respond politely and naturally.

RULES:
- Be conversational
- Keep it short (1–2 lines)
- If possible, gently guide them back to finance topics
- DO NOT refuse harshly
- DO NOT mention restrictions explicitly

Examples:
User: Tell me a joke  
→ I'm more focused on financial insights, but I can help you analyze revenue, profit, and business trends.

User: Who are you?  
→ I'm an AI Financial Analyst designed to help you understand business performance and financial data.

Now respond:
"""