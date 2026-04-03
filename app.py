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
        "Which product and customer segment combination is the most profitable, and why?",
    ]

    for i, ex in enumerate(examples):
        if st.button(ex, key=f"example_{i}"):
            st.session_state.pending_query = ex
            st.rerun()

    st.markdown("---")

    st.markdown("### ⚡ Quick Picks")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("📈 Trends"):
            st.session_state.pending_query = "Show revenue trend over time"
            st.rerun()

        if st.button("🌍 Regions"):
            st.session_state.pending_query = "Compare profit across regions"
            st.rerun()

    with col2:
        if st.button("🏆 Top"):
            st.session_state.pending_query = "Top 5 products by profit"
            st.rerun()

        if st.button("💰 Drivers"):
            st.session_state.pending_query = "What are the key drivers of profit?"
            st.rerun()

    st.markdown("---")

    show_intro = st.checkbox("📘 Show Guide", value=not st.session_state.messages)

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

# ---------------- CHART ---------------- #
def render_chart(df, chart_spec):
    try:
        chart_df = df[[chart_spec["x"], chart_spec["y"]]].set_index(chart_spec["x"])
        st.markdown("### 📊 Visualization")

        if chart_spec["type"] == "line":
            st.line_chart(chart_df)
        elif chart_spec["type"] == "bar":
            st.bar_chart(chart_df)
        elif chart_spec["type"] == "area":
            st.area_chart(chart_df)
        elif chart_spec["type"] == "pie":
            import matplotlib.pyplot as plt
            fig, ax = plt.subplots()
            chart_df[chart_spec["y"]].plot.pie(ax=ax, autopct='%1.1f%%')
            ax.set_ylabel("")
            st.pyplot(fig)
    except:
        pass

# ---------------- INPUT ---------------- #
user_input = st.chat_input("Ask your financial question...")

if st.session_state.pending_query:
    user_input = st.session_state.pending_query
    st.session_state.pending_query = None

## ---------------- PROCESS ---------------- #
if user_input:

    st.session_state.messages.append({"role": "user", "content": user_input})

    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):

        with st.spinner("🤖 Thinking..."):
            output = run_agent(user_input, schema)

        summary = (
            output.get("direct_answer")
            or output.get("summary")
            or output.get("message")
            or output.get("error")
            or "No clear answer could be generated."
        )

        insight = output.get("insight")
        evaluation = output.get("evaluation")
        chart_spec = output.get("chart")

        st.markdown("📌 **Summary**")

        if summary and str(summary).strip().lower() != "none":
            st.markdown(summary)
        else:
            st.warning("No meaningful summary could be generated.")

        rows = output.get("rows")
        columns = output.get("columns")

        is_data_response = rows and columns

        if is_data_response:

            df = pd.DataFrame(rows, columns=columns)

            if not df.empty:

                # SORT
                if df.shape[1] >= 2:
                    df = df.sort_values(by=df.columns[1], ascending=False)

                # TABLE
                st.markdown("### 📋 Data Snapshot")
                st.dataframe(df, use_container_width=True, hide_index=True)

                # KPI
                if len(df) > 1 and df.shape[1] >= 2:
                    val1 = df.iloc[0, 1]
                    val2 = df.iloc[1, 1]

                    if isinstance(val1, (int, float)) and isinstance(val2, (int, float)) and val2 != 0:
                        pct = ((val1 - val2) / val2) * 100

                        st.markdown(f"""
                        <div style="background:#f1f5f9;padding:10px;border-radius:8px;margin-top:8px;">
                        📊 <b>{df.iloc[0,0]}</b> leads <b>{df.iloc[1,0]}</b> by <b>{pct:.1f}%</b>
                        </div>
                        """, unsafe_allow_html=True)

                # INSIGHTS
                if insight and insight.strip().upper() != "NONE":
                    st.markdown("### 💡 Insights")
                    for line in insight.split("\n"):
                        if line.strip():
                            st.markdown(f"- {line.strip().lstrip('- ')}")

                # CHART
                if chart_spec:
                    render_chart(df, chart_spec)
                else:
                    st.markdown("### 📊 Visualization")
                    st.bar_chart(df.set_index(df.columns[0])[df.columns[1]])

                # CONFIDENCE
                if evaluation:
                    score = evaluation.get("overall")
                    if score >= 4:
                        st.success("✅ High Confidence")
                    elif score == 3:
                        st.warning("⚠️ Medium Confidence")
                    else:
                        st.error("❌ Low Confidence")

            else:
                st.info("No relevant data found for this query.")


        # FEEDBACK
        st.markdown("##### Was this helpful?")
        col1, col2, _ = st.columns([1,1,4])

        with col1:
            if st.button("👍", key=f"up_{len(st.session_state.messages)}"):
                log_feedback({"query": user_input, "response": summary, "feedback": "up"})
                st.toast("Thanks!")

        with col2:
            if st.button("👎", key=f"down_{len(st.session_state.messages)}"):
                log_feedback({"query": user_input, "response": summary, "feedback": "down"})
                st.toast("Noted!")

    st.session_state.messages.append({"role": "assistant", "content": summary})