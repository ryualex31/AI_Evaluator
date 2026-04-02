from agent.orchestrator import run_agent

# ---------------- SCHEMA ---------------- #
schema = """
financials(
    date, month, year,
    region, country,
    product, category,
    customer_type, supplier,
    units_sold, discount,
    revenue, cost, profit, profit_margin
)
"""


def test_query(query):
    print("\n" + "=" * 60)
    print(f"QUERY: {query}")

    result = run_agent(query, schema)

    # ---------------- MESSAGE ---------------- #
    if "message" in result:
        print("\n💬 RESPONSE:")
        print(result["message"])
        return

    # ---------------- ERROR ---------------- #
    if "error" in result:
        print("\n❌ ERROR:")
        print(result["error"])
        return

    # ---------------- ANSWER ---------------- #
    print("\n🧾 ANSWER:")
    print(result["direct_answer"])

    # ---------------- DATA ---------------- #
    print("\n📊 DATA:")
    print(result["table"])

    # ---------------- INSIGHT ---------------- #
    if result.get("insight"):
        print("\n🧠 INSIGHT:")
        print(result["insight"])

    # ---------------- EVALUATION (OPTIONAL) ---------------- #
    if result.get("evaluation"):
        eval_data = result["evaluation"]

        print("\n🔍 EVALUATION:")
        print(f"Accuracy: {eval_data.get('accuracy')}")
        print(f"Coverage: {eval_data.get('coverage')}")
        print(f"Faithfulness: {eval_data.get('faithfulness')}")
        print(f"Clarity: {eval_data.get('clarity')}")
        print(f"Overall: {eval_data.get('overall')}")

    # ---------------- RETRIES ---------------- #
    print(f"\n🔁 Retries used: {result['retries']}")


# ---------------- TEST RUN ---------------- #
if __name__ == "__main__":

    test_query("Total revenue by region")
    test_query("Top 3 products by profit")
    test_query("Revenue trend over months")

    # Non-finance
    test_query("Tell me a joke")
    test_query("Who are you?")
    test_query("What is the capital of France?")
    test_query("Hi")