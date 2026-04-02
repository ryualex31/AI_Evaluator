import streamlit as st
import pandas as pd
import os
import uuid
from agent.orchestrator import run_agent
from utils.logger import log_feedback

# ---------------- CONFIG ---------------- #
st.set_page_config(
    page_title="AI Financial Analyst",
    layout="wide"
)

# ---------------- SESSION ---------------- #
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

# ---------------- LOGIN ---------------- #
def check_login():

    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if st.session_state.authenticated:
        return True

    st.markdown("## 🔐 Login Required")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if (
            username == os.getenv("APP_USERNAME")
            and password == os.getenv("APP_PASSWORD")
        ):
            st.session_state.authenticated = True
            st.success("Login successful!")
            st.rerun()
        else:
            st.error("Invalid credentials")

    return False


if not check_login():
    st.stop()

# ---------------- STYLING ---------------- #
st.markdown("""
<style>
body {
    background-color: #f8fafc;
}

.main-title {
    font-size: 2rem;
    font-weight: 600;
    color: #111827;
}

.subtitle {
    color: #6b7280;
    margin-bottom: 20px;
}

.card {
    background-color: white;
    padding: 18px;
    border-radius: 12px;
    border: 1px solid #e5e7eb;
    box-shadow: 0px 2px 6px rgba(0,0,0,0.04);
}
</style>
""", unsafe_allow_html=True)

# ---------------- LOGOUT ---------------- #
with st.sidebar:
    if st.button("🚪 Logout"):
        st.session_state.authenticated = False
        st.rerun()

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

# ---------------- HEADER ---------------- #
st.markdown('<div class="main-title">💰 AI Financial Analyst</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Ask finance-related questions and get business insights instantly</div>', unsafe_allow_html=True)

# ---------------- SESSION QUERY ---------------- #
if "query" not in st.session_state:
    st.session_state.query = ""

# ---------------- EXAMPLES ---------------- #
st.markdown("### 💡 Example Queries")

examples = [
    "Total revenue by region",
    "Top 3 products by profit",
    "Revenue trend over months",
    "Which region has highest profit?",
    "Profit margin by category",
    "Which customer segment is most valuable?"
]

cols = st.columns(3)

for i, ex in enumerate(examples):
    if cols[i % 3].button(ex):
        st.session_state.query = ex

# ---------------- INPUT ---------------- #
query = st.text_input(
    "Ask your question",
    value=st.session_state.query,
    placeholder="e.g. Top 3 products by profit"
)

run = st.button("Analyze")

# ---------------- OUTPUT ---------------- #
if run:

    if not query.strip():
        st.info("Please enter a query.")
    else:
        with st.spinner("Analyzing financial data..."):
            output = run_agent(query, schema)

        # 💬 Conversational
        if "message" in output:
            st.markdown(
                f'<div class="card">{output["message"]}</div>',
                unsafe_allow_html=True
            )

        # ❌ Error
        elif "error" in output:
            st.markdown(
                f'<div class="card">⚠️ {output["error"]}</div>',
                unsafe_allow_html=True
            )

        # ✅ Success
        else:

            # 🧾 DIRECT ANSWER
            st.markdown("### 🧾 Answer")
            st.markdown(
                f'<div class="card"><b>{output["direct_answer"]}</b></div>',
                unsafe_allow_html=True
            )

            # 📊 DATA
            st.markdown("### 📊 Data")
            st.markdown(output["table"])

            # 🧠 INSIGHT
            if output.get("insight"):
                st.markdown("### 🧠 Insight")
                st.markdown(
                    f'<div class="card">{output["insight"]}</div>',
                    unsafe_allow_html=True
                )

            # 🔍 EVALUATION (OPTIONAL)
            if output.get("evaluation"):
                with st.expander("🔍 Show Evaluation (Optional)"):

                    eval_data = output["evaluation"]

                    col1, col2, col3, col4 = st.columns(4)

                    col1.metric("Accuracy", eval_data.get("accuracy"))
                    col2.metric("Coverage", eval_data.get("coverage"))
                    col3.metric("Faithfulness", eval_data.get("faithfulness"))
                    col4.metric("Clarity", eval_data.get("clarity"))

                    st.markdown(f"**Overall Score:** {eval_data.get('overall')}")

                    if eval_data.get("reason"):
                        st.markdown(
                            f'<div class="card">{eval_data["reason"]}</div>',
                            unsafe_allow_html=True
                        )

            # 👍 👎 FEEDBACK
            st.markdown("### 👍 Feedback")

            col1, col2 = st.columns(2)

            if col1.button("👍 Helpful"):
                log_feedback({
                    "session_id": st.session_state.session_id,
                    "query": query,
                    "response": output.get("direct_answer"),
                    "feedback": "positive"
                })
                st.success("Thanks for your feedback!")

            if col2.button("👎 Not Helpful"):
                log_feedback({
                    "session_id": st.session_state.session_id,
                    "query": query,
                    "response": output.get("direct_answer"),
                    "feedback": "negative"
                })
                st.warning("Thanks! We'll improve.")

            st.caption(f"Retries used: {output['retries']}")