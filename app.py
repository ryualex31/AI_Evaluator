import streamlit as st
import pandas as pd
import uuid
import re

from agent.orchestrator import run_agent

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
    border-radius: 10px;
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

    st.markdown("### Example Queries")

    examples = [
        "Total revenue by region",
        "Top 3 products by profit",
        "Revenue trend over months"
    ]

    for i, ex in enumerate(examples):
        if st.button(ex, key=f"example_{i}"):
            st.session_state.messages = [{"role": "user", "content": ex}]
            st.rerun()

    st.markdown("---")

    st.markdown("### Insights")

    insights = [
        "Revenue trends",
        "Profit drivers",
        "Regional performance",
        "Customer segmentation"
    ]

    for i, item in enumerate(insights):
        if st.button(item, key=f"insight_{i}"):
            st.session_state.messages = [{"role": "user", "content": item}]
            st.rerun()

    st.markdown("---")

    if st.button("🚪 Logout"):
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

# ---------------- DISPLAY CHAT ---------------- #
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ---------------- USER INPUT ---------------- #
user_input = st.chat_input("Ask your financial question...")

if user_input:

    # Show user message
    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })

    with st.chat_message("user"):
        st.markdown(user_input)

    # Generate response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            output = run_agent(user_input, schema)

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

        # Display answer
        st.markdown(answer)

        # Table (if exists)
        if table:
            try:
                df = pd.read_html(table)[0]
                st.dataframe(df, use_container_width=True)
            except:
                st.markdown(table)

        # Insight (if exists)
        if insight:
            st.info(f"💡 {insight}")

    # Save assistant response (ONLY answer text for simplicity)
    st.session_state.messages.append({
        "role": "assistant",
        "content": answer
    })