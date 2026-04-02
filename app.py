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

if "query" not in st.session_state:
    st.session_state.query = ""

# ---------------- STYLING ---------------- #
st.markdown("""
<style>
html, body, [class*="css"] {
    background-color: #ffffff !important;
    color: #111827;
}

.card {
    background-color: white;
    padding: 18px;
    border-radius: 12px;
    border: 1px solid #e5e7eb;
    box-shadow: 0px 2px 6px rgba(0,0,0,0.05);
    margin-bottom: 15px;
}

.sidebar-card {
    background-color: #f9fafb;
    padding: 15px;
    border-radius: 10px;
    border: 1px solid #e5e7eb;
    margin-bottom: 10px;
}

.block-container {
    padding-top: 2rem;
}
</style>
""", unsafe_allow_html=True)

# ---------------- LOGIN ---------------- #
def check_login():

    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if st.session_state.authenticated:
        return True

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        st.markdown("""
        <div style="
            background-color:white;
            padding:30px;
            border-radius:12px;
            border:1px solid #e5e7eb;
            box-shadow:0px 4px 12px rgba(0,0,0,0.05);
        ">
        """, unsafe_allow_html=True)

        st.markdown("### 🔐 Login")

        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("→"):
            if (
                username == os.getenv("APP_USERNAME")
                and password == os.getenv("APP_PASSWORD")
            ):
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("Invalid credentials")

        st.markdown("</div>", unsafe_allow_html=True)

    return False


if not check_login():
    st.stop()

# ---------------- SIDEBAR ---------------- #
with st.sidebar:
    st.markdown("## 📌 Example Queries")

    examples = [
        "Total revenue by region",
        "Top 3 products by profit",
        "Revenue trend over months",
        "Profit margin by category",
        "Which region is most profitable?"
    ]

    for ex in examples:
        if st.button(ex):
            st.session_state.query = ex

    st.markdown("---")

    st.markdown("## 📊 Insights You Can Explore")

    st.markdown("""
    <div class="sidebar-card">
    💰 Revenue trends  
    📈 Profit drivers  
    🌍 Regional performance  
    🧾 Customer segmentation  
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    if st.button("🚪 Logout"):
        st.session_state.authenticated = False
        st.rerun()

# ---------------- HEADER ---------------- #
st.markdown("## 💰 AI Financial Analyst")
st.caption("Ask financial questions and get instant business insights")

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

# ---------------- INPUT (CHAT STYLE) ---------------- #
col1, col2 = st.columns([10, 1])

with col1:
    query = st.text_input(
        "",
        value=st.session_state.query,
        placeholder="Ask your financial question..."
    )

with col2:
    submit = st.button("➤")

# ---------------- OUTPUT ---------------- #
if query or submit:

    if not query.strip():
        st.stop()

    with st.spinner(""):
        output = run_agent(query, schema)

    # 💬 Conversational
    if "message" in output:
        st.markdown(f'<div class="card">{output["message"]}</div>', unsafe_allow_html=True)

    # ❌ Error
    elif "error" in output:
        st.markdown(f'<div class="card">⚠️ {output["error"]}</div>', unsafe_allow_html=True)

    # ✅ Success
    else:

        # 🧾 ANSWER
        st.markdown("### 🧾 Answer")
        st.markdown(
            f'<div class="card"><b>{output["direct_answer"]}</b></div>',
            unsafe_allow_html=True
        )

        # 📊 DATA
        st.markdown("### 📊 Data")

        df = pd.DataFrame(output["rows"], columns=output["columns"])

        st.dataframe(
            df.style.format({
                col: "{:,.0f}" for col in df.select_dtypes("number").columns
            }),
            use_container_width=True,
            height=300
        )

        # 🧠 INSIGHT
        if output.get("insight"):
            st.markdown("### 🧠 Insight")
            st.markdown(
                f'<div class="card">{output["insight"]}</div>',
                unsafe_allow_html=True
            )

        # 🔍 EVALUATION
        if output.get("evaluation"):
            with st.expander("🔍 Show Evaluation"):

                eval_data = output["evaluation"]

                col1, col2, col3, col4 = st.columns(4)

                col1.metric("Accuracy", eval_data.get("accuracy"))
                col2.metric("Coverage", eval_data.get("coverage"))
                col3.metric("Faithfulness", eval_data.get("faithfulness"))
                col4.metric("Clarity", eval_data.get("clarity"))

                st.markdown(f"**Overall Score:** {eval_data.get('overall')}")

        # 👍 👎 FEEDBACK
        st.markdown("### 👍 Feedback")

        col1, col2 = st.columns(2)

        if col1.button("👍"):
            log_feedback({
                "session_id": st.session_state.session_id,
                "query": query,
                "response": output.get("direct_answer"),
                "feedback": "positive"
            })
            st.success("Thanks!")

        if col2.button("👎"):
            log_feedback({
                "session_id": st.session_state.session_id,
                "query": query,
                "response": output.get("direct_answer"),
                "feedback": "negative"
            })
            st.warning("Noted!")

        st.caption(f"Retries used: {output['retries']}")