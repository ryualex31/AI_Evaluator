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

# ---------------- STYLING ---------------- #
st.markdown("""
<style>
.block-container {
    padding-top: 2rem;
}

.stChatMessage {
    padding: 12px !important;
    border-radius: 12px;
}

[data-testid="stSidebar"] {
    background-color: #f9fafb;
}
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
        "Which product and customer segment combination is the most profitable, and why?",
        "Which supplier is associated with the lowest profit margins, and what could be the reason?"
    ]

    for i, ex in enumerate(examples):
        if st.button(ex, key=f"example_{i}"):
            st.session_state.messages = [{"role": "user", "content": ex}]
            st.rerun()

    st.markdown("---")

    if st.button("🔄 Reset Chat"):
        st.session_state.messages = []
        st.rerun()

    if st.button("🚪 Logout"):
        st.session_state.authenticated = False
        st.rerun()

# ---------------- HEADER ---------------- #
st.markdown("## 📊 AI Financial Analyst")
st.caption("Ask questions about revenue, profit, and business performance")

# ---------------- EMPTY STATE ---------------- #
if not st.session_state.messages:
    st.markdown("""
    ### 👋 Welcome!
    
    Try asking:
    - 📈 Revenue trends over time  
    - 🌍 Profit by region  
    - 🧠 Key profit drivers  
    """)

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

# ---------------- CHART HELPER ---------------- #
def generate_chart(df, user_query):
    query = user_query.lower()

    try:
        # ----------- TIME SERIES ----------- #
        if "month" in df.columns or "date" in df.columns:
            if any(word in query for word in ["trend", "month", "over time", "q4"]):

                x_col = "month" if "month" in df.columns else "date"
                y_col = None

                for col in ["revenue", "profit"]:
                    if col in df.columns:
                        y_col = col
                        break

                if x_col and y_col:
                    st.markdown("### 📈 Trend Analysis")
                    st.line_chart(df.set_index(x_col)[y_col])

        # ----------- BAR CHART ----------- #
        elif any(col in df.columns for col in ["region", "product", "supplier"]):

            x_col = None
            for col in ["region", "product", "supplier"]:
                if col in df.columns:
                    x_col = col
                    break

            y_col = None
            for col in ["revenue", "profit"]:
                if col in df.columns:
                    y_col = col
                    break

            if x_col and y_col:
                st.markdown("### 📊 Comparison View")
                st.bar_chart(df.set_index(x_col)[y_col])

    except Exception:
        pass

# ---------------- CHAT DISPLAY ---------------- #
avatar_map = {
    "user": "🧑‍💼",
    "assistant": "🤖"
}

for msg in st.session_state.messages:
    with st.chat_message(msg["role"], avatar=avatar_map[msg["role"]]):
        st.markdown(msg["content"])

# ---------------- USER INPUT ---------------- #
user_input = st.chat_input("Ask your financial question...")

if user_input:

    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })

    with st.chat_message("user", avatar="🧑‍💼"):
        st.markdown(user_input)

    with st.chat_message("assistant", avatar="🤖"):

        with st.spinner("🤖 Analyzing your data..."):
            output = run_agent(user_input, schema)

        # Handle response
        if "message" in output:
            answer = output["message"]
            table = None
            insight = None

        elif "error" in output:
            answer = output["error"]
            table = None
            insight = None

        else:
            answer = output["direct_answer"]
            table = output.get("table")
            insight = output.get("insight")

        # Answer
        st.markdown(answer)

        # Table + Chart
        if table:
            try:
                df = pd.read_html(table)[0]

                st.markdown("### 📊 Data Snapshot")
                st.dataframe(df, use_container_width=True)

                # 🔥 Auto chart
                generate_chart(df, user_input)

            except:
                st.markdown(table)

        # Insight (filtered)
        if insight:
            clean_answer = answer.lower().replace("$", "").replace(",", "").strip()
            clean_insight = insight.lower().replace("$", "").replace(",", "").strip()

            if clean_answer != clean_insight:
                st.markdown(f"""
                <div style="
                    background-color:#eef6ff;
                    padding:12px;
                    border-radius:10px;
                    border:1px solid #c7ddff;
                    margin-top:10px;
                ">
                💡 <b>Insight:</b><br>{insight}
                </div>
                """, unsafe_allow_html=True)

        # ---------------- FEEDBACK ---------------- #
        st.markdown("##### Was this helpful?")

        col1, col2, col3 = st.columns([1,1,8])

        with col1:
            if st.button("👍", key=f"up_{len(st.session_state.messages)}"):
                log_feedback({
                    "query": user_input,
                    "response": answer,
                    "feedback": "up"
                })
                st.success("Feedback recorded")

        with col2:
            if st.button("👎", key=f"down_{len(st.session_state.messages)}"):
                log_feedback({
                    "query": user_input,
                    "response": answer,
                    "feedback": "down"
                })
                st.warning("Feedback recorded")

    st.session_state.messages.append({
        "role": "assistant",
        "content": answer
    })