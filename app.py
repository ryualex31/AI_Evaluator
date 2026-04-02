import streamlit as st
import pandas as pd
import uuid
import re

from agent.orchestrator import run_agent
from utils.logger import log_feedback

# ---------------- CONFIG ---------------- #
st.set_page_config(page_title="AI Financial Analyst", layout="wide")

# ---------------- SESSION ---------------- #
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# ---------------- STYLING ---------------- #
st.markdown("""
<style>

.block-container {
    padding-top: 2rem;
}

.card {
    background-color: #ffffff;
    color: #111827;
    padding: 14px;
    border-radius: 10px;
    border: 1px solid #e5e7eb;
    margin-bottom: 8px;
}

.user-card {
    background-color: #f1f5f9;
    padding: 10px;
    border-radius: 10px;
    margin-bottom: 4px;
}

.sidebar-card {
    background-color: #f9fafb;
    padding: 15px;
    border-radius: 10px;
    border: 1px solid #e5e7eb;
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

        st.markdown("### Sign In")

        email = st.text_input("Email")
        password = st.text_input("Password", type="password")

        if st.button("→"):
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

    st.markdown("### Example Queries")

    examples = [
        "Total revenue by region",
        "Top 3 products by profit",
        "Revenue trend over months"
    ]

    for ex in examples:
        if st.button(ex):
            st.session_state.chat_history.append({"query": ex})

    st.markdown("---")

    st.markdown("### Insights")

    st.markdown("""
    <div class="sidebar-card">
    <ul>
    <li>Revenue trends</li>
    <li>Profit drivers</li>
    <li>Regional performance</li>
    <li>Customer segmentation</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)

    insights = [
        "Revenue trends",
        "Profit drivers",
        "Regional performance",
        "Customer segmentation"
    ]

    for item in insights:
        if st.button(item):
            st.session_state.chat_history.append({"query": item})

    st.markdown("---")

    if st.button("Clear Chat"):
        st.session_state.chat_history = []
        st.rerun()

    if st.button("Logout"):
        st.session_state.authenticated = False
        st.rerun()

# ---------------- HEADER ---------------- #
st.markdown("## AI Financial Analyst")

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

# ---------------- PROCESS NEW QUERY ---------------- #
if st.session_state.chat_history and "answer" not in st.session_state.chat_history[-1]:

    last_query = st.session_state.chat_history[-1]["query"]

    with st.spinner(""):
        output = run_agent(last_query, schema)

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
        table = output["table"]
        insight = output.get("insight")

    st.session_state.chat_history[-1].update({
        "answer": answer,
        "table": table,
        "insight": insight
    })

# ---------------- CHAT DISPLAY ---------------- #
st.markdown("### Conversation")

for chat in st.session_state.chat_history:

    st.markdown(f'<div class="user-card">{chat["query"]}</div>', unsafe_allow_html=True)

    if "answer" in chat:
        st.markdown(f'<div class="card">{chat["answer"]}</div>', unsafe_allow_html=True)

        if chat.get("table"):
            st.markdown(chat["table"])

        if chat.get("insight"):
            st.markdown(f'<div class="card">{chat["insight"]}</div>', unsafe_allow_html=True)

# ---------------- INPUT ---------------- #
col1, col2, col3 = st.columns([10,1,1])

with col1:
    user_input = st.text_input("", placeholder="Ask your financial question...")

with col2:
    send = st.button("➤")

with col3:
    refresh = st.button("↻")

if refresh:
    st.session_state.chat_history = []
    st.rerun()

if send and user_input:
    st.session_state.chat_history.append({"query": user_input})
    st.rerun()