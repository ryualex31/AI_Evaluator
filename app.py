import streamlit as st
import pandas as pd
from agent.orchestrator import run_agent

# ---------------- CONFIG ---------------- #
st.set_page_config(
    page_title="AI Financial Analyst",
    layout="wide"
)

# ---------------- STYLING ---------------- #
st.markdown("""
<style>
.main-title {
    font-size: 2.2rem;
    font-weight: 700;
}
.subtle {
    color: #6b7280;
}
.card {
    padding: 1rem;
    border-radius: 12px;
    background-color: #f9fafb;
    border: 1px solid #e5e7eb;
}
</style>
""", unsafe_allow_html=True)

# ---------------- HEADER ---------------- #
st.markdown('<div class="main-title">💰 AI Financial Analyst</div>', unsafe_allow_html=True)
st.markdown('<div class="subtle">Ask finance questions and get instant insights</div>', unsafe_allow_html=True)

st.divider()

# ---------------- SESSION STATE ---------------- #
if "history" not in st.session_state:
    st.session_state.history = []

if "query" not in st.session_state:
    st.session_state.query = ""

# ---------------- EXAMPLES ---------------- #
st.markdown("### 💡 Try these")

cols = st.columns(3)

examples = [
    "Total revenue by region",
    "Top 3 products by profit",
    "Monthly revenue trend",
    "Profit by category",
    "Revenue in India",
    "Which region performs best?"
]

for i, ex in enumerate(examples):
    if cols[i % 3].button(ex):
        st.session_state.query = ex

# ---------------- INPUT ---------------- #
query = st.text_input(
    "Ask your question:",
    value=st.session_state.query,
    placeholder="e.g. Show revenue trends by region"
)

# Schema
schema = """
financials(
    date, month, year, region, country,
    product, category, revenue, cost, profit, customer_type
)
"""

# ---------------- RUN ---------------- #
if st.button("🚀 Analyze"):

    if not query.strip():
        st.info("Please enter a question.")
    else:
        with st.spinner("Analyzing financial data..."):
            output = run_agent(query, schema)

        # Save history
        st.session_state.history.append((query, output))

# ---------------- OUTPUT ---------------- #
if st.session_state.history:

    st.divider()
    st.markdown("## 📊 Results")

    # Show latest response
    last_query, output = st.session_state.history[-1]

    st.markdown(f"**🧑 Query:** {last_query}")

    # Conversational responses
    if "message" in output:
        st.markdown(f"<div class='card'>{output['message']}</div>", unsafe_allow_html=True)

    # Errors
    elif "error" in output:
        st.markdown(f"<div class='card'>⚠️ {output['error']}</div>", unsafe_allow_html=True)

    # Success
    else:
        df = pd.DataFrame(output["rows"], columns=output["columns"])

        col1, col2 = st.columns([2, 1])

        # 📊 Table
        with col1:
            st.markdown("### 📈 Data")
            st.dataframe(df, use_container_width=True, height=400)

        # 🧠 Insight card
        with col2:
            st.markdown("### 🧠 Insight")
            st.markdown(
                f"<div class='card'>{output['insight']}</div>",
                unsafe_allow_html=True
            )

        st.caption(f"Retries used: {output['retries']}")

# ---------------- HISTORY ---------------- #
if len(st.session_state.history) > 1:
    st.divider()
    st.markdown("## 🕘 Previous Queries")

    for q, _ in reversed(st.session_state.history[:-1]):
        st.markdown(f"- {q}")