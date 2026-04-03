import streamlit as st
import pandas as pd
import uuid
import re

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

if "messages" not in st.session_state:
    st.session_state.messages = []

if "pending_query" not in st.session_state:
    st.session_state.pending_query = None

# ---------------- STYLING ---------------- #
st.markdown("""
<style>
.block-container { padding-top: 2rem; }
.stChatMessage { padding: 12px !important; border-radius: 12px; }
[data-testid="stSidebar"] { background-color: #f9fafb; }
</style>
""", unsafe_allow_html=True)

# ---------------- LOGIN ---------------- #
def is_valid_email(email):
    return re.match(r"[^@]+@[^@]+\.[^@]+", email)


def check_login():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if st.session_state.authenticated:
        return True

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        st.markdown("""
        <div style="background:white;padding:30px;border-radius:12px;
        border:1px solid #e5e7eb;">
        """, unsafe_allow_html=True)

        st.markdown("### 🔐 Sign In")

        email = st.text_input("Email")
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            if not email or not password:
                st.error("Please fill all fields")
            elif not is_valid_email(email):
                st.error("Enter valid email")
            else:
                st.session_state.authenticated = True
                st.session_state.user_email = email
                st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)

    return False


if not check_login():
    st.stop()

# ---------------- SIDEBAR ---------------- #
with st.sidebar:

    st.markdown(f"👤 {st.session_state.get('user_email','')}")

    st.markdown("### 🧪 Example Queries")

    examples = [
        "How much was the revenue change month over month in 2024, and did we see a spike in Q4?",
        "Which region contributed the most to profit in 2024, and how does it compare to others?",
        "Which product and customer segment combination is the most profitable, and why?"
    ]

    for i, ex in enumerate(examples):
        if st.button(ex, key=f"example_{i}"):
            st.session_state.pending_query = ex
            st.rerun()

    st.markdown("---")

    if st.button("🔄 Reset Chat"):
        st.session_state.messages = []
        st.session_state.pending_query = None
        st.rerun()

    if st.button("🚪 Logout"):
        st.session_state.authenticated = False
        st.rerun()

# ---------------- HEADER ---------------- #
st.markdown("## 📊 AI Financial Analyst")
st.caption("Analyze business performance using natural language queries")

# ---------------- INTRO ---------------- #
if not st.session_state.messages:
    st.markdown("""
    <div style="
        background-color:#f8fafc;
        padding:16px;
        border-radius:10px;
        border:1px solid #e5e7eb;
        margin-bottom:12px;
    ">

    📊 <b>AI Financial Analyst for a Global Business</b><br><br>

    You are analyzing a <b>global business dataset</b> covering products, suppliers, customers, and regions.

    <br>

    <b>📊 What data is available:</b>
    <ul>
    <li>🌍 Regions & country-level performance</li>
    <li>📦 Products & categories</li>
    <li>🏭 Suppliers & customer segments</li>
    <li>📅 Time-based metrics (monthly & yearly)</li>
    </ul>

    <b>📈 Key metrics you can explore:</b>
    <ul>
    <li>Revenue, cost, and profit</li>
    <li>Profit margins and growth trends</li>
    <li>Top-performing suppliers, products, and regions</li>
    <li>Comparative performance analysis</li>
    </ul>

    <b>🧠 Example questions:</b>
    <ul>
    <li>Which supplier generated the highest revenue?</li>
    <li>Which region is most profitable and how does it compare?</li>
    <li>What are the key drivers of profit?</li>
    <li>How did revenue trend over time?</li>
    </ul>

    </div>
    """, unsafe_allow_html=True)

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

# ---------------- CHART ---------------- #
def generate_chart(df, user_query):
    query = user_query.lower()

    try:
        if "month" in df.columns or "date" in df.columns:
            if any(word in query for word in ["trend", "month", "over time", "q4"]):
                x_col = "month" if "month" in df.columns else "date"

                for col in ["revenue", "profit"]:
                    if col in df.columns:
                        st.markdown("### 📈 Trend Analysis")
                        st.line_chart(df.set_index(x_col)[col])
                        return

        elif any(col in df.columns for col in ["region", "product", "supplier"]):
            for x_col in ["region", "product", "supplier"]:
                if x_col in df.columns:
                    for col in ["revenue", "profit"]:
                        if col in df.columns:
                            st.markdown("### 📊 Comparison View")
                            st.bar_chart(df.set_index(x_col)[col])
                            return
    except:
        pass

# ---------------- CHAT DISPLAY ---------------- #
avatar_map = {"user": "🧑‍💼", "assistant": "🤖"}

for msg in st.session_state.messages:
    with st.chat_message(msg["role"], avatar=avatar_map[msg["role"]]):
        st.markdown(msg["content"])

# ---------------- INPUT ---------------- #
user_input = st.chat_input("Ask your financial question...")

if st.session_state.pending_query:
    user_input = st.session_state.pending_query
    st.session_state.pending_query = None

# ---------------- PROCESS ---------------- #
if user_input:

    st.session_state.messages.append({"role": "user", "content": user_input})

    with st.chat_message("user", avatar="🧑‍💼"):
        st.markdown(user_input)

    with st.chat_message("assistant", avatar="🤖"):

        with st.spinner("🤖 Analyzing your data..."):
            output = run_agent(user_input, schema)

        answer = output.get("direct_answer") or output.get("message") or output.get("error")
        table = output.get("table")
        insight = output.get("insight")
        evaluation = output.get("evaluation")
        sql_query = output.get("sql_query")

        # ANSWER
        st.markdown(f"📌 **Answer:** {answer}")

        # CONFIDENCE
        if evaluation and isinstance(evaluation, dict):
            score = evaluation.get("overall", None)

            if score is not None:
                if score >= 4:
                    st.success("✅ High Confidence")
                elif score == 3:
                    st.warning("⚠️ Medium Confidence")
                else:
                    st.error("❌ Low Confidence")

        # TABLE + CHART
        if table:
            try:
                df = pd.read_html(table)[0]
                st.markdown("### 📊 Data Snapshot")
                st.dataframe(df, use_container_width=True)
                generate_chart(df, user_input)

                if len(df) > 1 and df.shape[1] >= 2:
                    top = df.iloc[0]
                    second = df.iloc[1]

                    if isinstance(top[1], (int, float)) and isinstance(second[1], (int, float)):
                        diff = top[1] - second[1]
                        pct = (diff / second[1]) * 100 if second[1] != 0 else 0

                        st.info(f"📊 {top[0]} leads over {second[0]} by {diff:,.0f} ({pct:.1f}%)")

            except:
                st.markdown(table)

        # INSIGHT
        if insight and insight.strip().upper() != "NONE":
            st.info(f"💡 {insight}")

        # SQL VIEW
        if sql_query:
            with st.expander("🔍 View SQL"):
                st.code(sql_query, language="sql")

        # ---------------- FEEDBACK (COMBINED) ---------------- #
        st.markdown("##### Was this helpful?")
        col1, col2, col3 = st.columns([1,1,4])

        with col1:
            if st.button("👍", key=f"up_{len(st.session_state.messages)}"):
                log_feedback({"query": user_input, "response": answer, "feedback": "up"})
                st.toast("Thanks for your feedback!")

        with col2:
            if st.button("👎", key=f"down_{len(st.session_state.messages)}"):
                log_feedback({"query": user_input, "response": answer, "feedback": "down"})
                st.toast("Feedback noted!")

    st.session_state.messages.append({"role": "assistant", "content": answer})