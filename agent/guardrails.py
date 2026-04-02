from utils.llm import call_llm

def classify_intent(query):
    prompt = f"""
You are an intent classifier.

Classify the user query into one of the following categories:

1. FINANCE_QUERY → related to financial data, revenue, profit, trends
2. GENERAL_QUERY → questions like "who are you", "what can you do"
3. IRRELEVANT_QUERY → jokes, casual chat, unrelated topics

Query: "{query}"

Respond with ONLY one label:
FINANCE_QUERY, GENERAL_QUERY, or IRRELEVANT_QUERY
"""
    response = call_llm(prompt).strip().upper()
    return response