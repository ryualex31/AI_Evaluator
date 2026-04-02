from agent.orchestrator import run_agent

schema = """
financials(
    date, month, year, region, country,
    product, category, revenue, cost, profit, customer_type
)
"""

def test_query(query):
    print("\n" + "="*50)
    print(f"QUERY: {query}")

    result = run_agent(query, schema)

    if "message" in result:
        print("\n💬 MESSAGE:")
        print(result["message"])

    elif "error" in result:
        print("\n❌ ERROR:")
        print(result["error"])

    else:
        print("\n📊 RESULT (first 5 rows):")
        for row in result["rows"][:5]:
            print(row)

        print("\n🧠 INSIGHT:")
        print(result["insight"])

        print(f"\n🔁 Retries used: {result['retries']}")


if __name__ == "__main__":
    test_query("Total revenue by region")
    test_query("Top 3 products by profit")
    test_query("Tell me a joke")
    test_query("Who are you?")