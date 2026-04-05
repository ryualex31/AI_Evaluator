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

if "messages" not in st.session_state:
    st.session_state.messages = []

if "pending_query" not in st.session_state:
    st.session_state.pending_query = None

if "is_processing" not in st.session_state:
    st.session_state.is_processing = False

if "run_query" not in st.session_state:
    st.session_state.run_query = None

if "feedback_done_for" not in st.session_state:
    st.session_state.feedback_done_for = set()

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

    col1, col2 = st.columns([1.2, 1])

    with col1:
        st.markdown("""
        <div style="
            height: 100%;
            background: linear-gradient(135deg, #0ea5e9, #6366f1);
            border-radius: 16px;
            padding: 40px;
            color: white;
        ">
            <h2>📊 AI Financial Analyst</h2>
            <p>Analyze business performance using natural language queries</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div style="background:white;padding:30px;border-radius:16px;border:1px solid #e5e7eb;">
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
    ]

    for i, ex in enumerate(examples):
        if st.button(ex, key=f"example_{i}", disabled=st.session_state.is_processing):
            st.session_state.pending_query = ex
            st.rerun()

    st.markdown("---")

    st.markdown("### ⚡ Quick Picks")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("📈 Trends", disabled=st.session_state.is_processing):
            st.session_state.pending_query = "Show revenue trend over time"
            st.rerun()

        if st.button("🌍 Regions", disabled=st.session_state.is_processing):
            st.session_state.pending_query = "Compare profit across regions"
            st.rerun()

    with col2:
        if st.button("🏆 Top", disabled=st.session_state.is_processing):
            st.session_state.pending_query = "Top 5 products by profit"
            st.rerun()

        if st.button("💰 Drivers", disabled=st.session_state.is_processing):
            st.session_state.pending_query = "What are the key drivers of profit?"
            st.rerun()

    st.markdown("---")

    show_intro = st.checkbox("📘 Show Guide", value=not st.session_state.messages)

    if st.button("🔄 Reset Chat", disabled=st.session_state.is_processing):
        st.session_state.messages = []
        st.rerun()

    if st.button("🚪 Logout"):
        st.session_state.authenticated = False
        st.rerun()

# ---------------- HEADER ---------------- #
st.markdown("## 📊 AI Financial Analyst")
st.caption("Analyze business performance using natural language queries")

# ---------------- INTRO ---------------- #
if show_intro:
    st.markdown("""
    <div style="
        background-color:#f8fafc;
        padding:18px;
        border-radius:12px;
        border:1px solid #e5e7eb;
        margin-bottom:16px;
        line-height:1.6;
    ">

    <h4>📊 AI Financial Analyst for a Global Business</h4>

    <p>
    You are analyzing a <b>global business dataset</b> covering products, suppliers, customers, and regions.
    </p>

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
schema = """financials(date, month, year, region, country, product, category, customer_type, supplier, units_sold, discount, revenue, cost, profit, profit_margin)"""

# ---------------- INPUT ---------------- #
user_input = st.chat_input(
    "Ask your financial question...",
    disabled=st.session_state.is_processing
)

if user_input and not st.session_state.is_processing:
    st.session_state.run_query = user_input
    st.session_state.is_processing = True
    st.rerun()

if st.session_state.pending_query and not st.session_state.is_processing:
    st.session_state.run_query = st.session_state.pending_query
    st.session_state.pending_query = None
    st.session_state.is_processing = True
    st.rerun()

# ---------------- RENDER CHAT ---------------- #
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):

        if msg["role"] == "user":
            st.markdown(msg["content"])

        else:
            st.markdown("📌 **Summary**")
            st.markdown(msg["summary"])

            # Insights
            if msg.get("insight") and msg["insight"].strip().upper() != "NONE":
                st.markdown("### 💡 Insights")
                for line in msg["insight"].split("\n"):
                    if line.strip():
                        st.markdown(line.strip())

            # Table + Chart
            if msg.get("rows") and msg.get("columns"):
                df = pd.DataFrame(msg["rows"], columns=msg["columns"])
                if not df.empty:
                    st.markdown("### 📋 Data Snapshot")
                    st.dataframe(df, use_container_width=True, hide_index=True)

                    st.markdown("### 📊 Visualization")
                    st.bar_chart(df.set_index(df.columns[0])[df.columns[1]])

            if msg.get("evaluation"):
                score = msg["evaluation"].get("overall")
                if score >= 4:
                    st.success("✅ High Confidence")
                elif score == 3:
                    st.warning("⚠️ Medium Confidence")
                else:
                    st.error("❌ Low Confidence")

            # OPTIONAL FEEDBACK
            msg_id = msg["id"]
            disabled = msg_id in st.session_state.feedback_done_for

            col1, col2, col3 = st.columns([0.08, 0.08, 0.84])

            if col1.button("👍", key=f"up_{msg_id}", disabled=disabled):
                log_feedback({"query": msg["query"], "response": msg["summary"], "feedback": "up"})
                st.session_state.feedback_done_for.add(msg_id)
                st.rerun()

            if col2.button("👎", key=f"down_{msg_id}", disabled=disabled):
                log_feedback({"query": msg["query"], "response": msg["summary"], "feedback": "down"})
                st.session_state.feedback_done_for.add(msg_id)
                st.rerun()

# ---------------- PROCESS ---------------- #
if st.session_state.run_query and st.session_state.is_processing:

    query = st.session_state.run_query

    st.session_state.messages.append({
        "role": "user",
        "content": query
    })

    with st.spinner("🤖 Thinking..."):
        output = run_agent(query, schema, user_email=st.session_state.get("user_email"))

    summary = (
        output.get("direct_answer")
        or output.get("summary")
        or output.get("message")
        or output.get("error")
        or "No clear answer."
    )

    message_obj = {
        "id": str(uuid.uuid4()),
        "role": "assistant",
        "query": query,
        "summary": summary,
        "rows": output.get("rows"),
        "columns": output.get("columns"),
        "insight": output.get("insight"),
        "evaluation": output.get("evaluation")
    }

    st.session_state.messages.append(message_obj)

    st.session_state.run_query = None
    st.session_state.is_processing = False

    st.rerun()