# 📊 AI Financial Analyst

An AI-powered conversational analytics system that enables business users to query financial data using natural language and receive instant, SQL-backed insights.

## 🔍 Business Impact

- Reduces dependency on data teams for ad-hoc queries  
- Reduces insight turnaround time from hours/days to seconds  
- Improves decision velocity for business teams  
- Enables self-serve analytics for non-technical stakeholders  

---

## 🎯 Why This Matters

This system demonstrates how AI can transform analytics into a self-serve, conversational experience.

It reduces operational bottlenecks, improves decision speed, and enables scalable access to data-driven insights across organizations.

---

## 🚀 Demo

👉 https://aicasestudy.azurewebsites.net/

---

## 🔐 Lightweight Login

- Email-based login for session simulation  
- Enables personalized interaction  
- Placeholder for production-grade authentication  

---

## ✨ Features

- 💬 Natural Language → SQL conversion  
- 📊 Instant data retrieval & visualization  
- 💡 AI-generated business insights  
- 🔁 Automatic SQL correction (retry mechanism)  
- 🧠 LLM-based response evaluation  
- 📝 Persistent logging for observability  

---

## 🧠 Example Queries

- Revenue trend over months  
- Top products by profit  
- Regional performance comparison  
- Monthly growth rate analysis  
- Profit margin by category  

---

## ⚙️ Run Locally

```bash
git clone <repo-link>
cd <repo>

pip install -r requirements.txt
streamlit run app.py
```

### 🔑 Environment Setup

Create a `.env` file:

```env
AZURE_OPENAI_API_KEY=your_key
AZURE_OPENAI_ENDPOINT=your_endpoint
AZURE_OPENAI_DEPLOYMENT=gpt-4o
AZURE_OPENAI_API_VERSION=2024-02-15-preview
```

---

## 🧰 Tech Stack

- **Frontend**: Streamlit  
- **Backend**: Python  
- **LLM**: Azure OpenAI  
- **Database**: SQLite  
- **Architecture**: LLM-powered agent pipeline  

---

## 🤖 Why LLM?

Traditional BI tools require predefined dashboards and SQL expertise, limiting flexibility for ad-hoc analysis.

LLMs enable:
- Natural language querying without technical knowledge  
- Dynamic SQL generation based on schema understanding  
- Automated insight generation beyond raw data  

This allows users to interact with data conversationally, without relying on data teams.

---

## 🏗️ System Architecture

The system is designed as a modular LLM-powered analytics pipeline:

### 1. Interaction Layer
- Streamlit UI for user queries  

### 2. Orchestration Layer (LLM-driven)
- Intent Classification  
- SQL Generation  
- Retry & Correction Loop  
- Response & Insight Generation  

### 3. Execution Layer
- SQLite database for financial data queries  

### 4. Evaluation Layer
- LLM-as-a-judge scoring (accuracy, faithfulness, etc.)  

### 5. Observability Layer
- Logging of all interactions for monitoring and improvement  

---

## ⚖️ Key Design Decisions & Trade-offs

- **LLM-first approach vs traditional BI tools**  
  → Enables flexible querying without predefined dashboards  

- **LLM-friendly schema (no joins)**  
  → Improves SQL accuracy and reduces hallucination risk  

- **SQLite vs Data Warehouse**  
  → Lightweight for MVP; can scale to Snowflake/BigQuery  

- **No RAG pipeline**  
  → Structured schema sufficient; avoids unnecessary complexity  

- **Retry-based SQL correction**  
  → Improves robustness without manual intervention  

---

## 🛡️ Reliability & Guardrails

- SQL validation before execution to prevent unsafe queries  
- Automatic retry mechanism for failed SQL generation  
- Query constraints (e.g., LIMIT clauses) to avoid large scans  
- Error logging for debugging and system improvement  

---

## 📝 Logging & Evaluation

The application includes a **production-ready SQLite-based logging system** to capture interactions, enable evaluation, and support continuous improvement.

---

## 📊 What is Logged

For every user query, the system captures:

- User query  
- Intent classification  
- Generated SQL query  
- SQL prompt used  
- Query results (preview)  
- Direct answer  
- Generated insights  
- Evaluation metrics (LLM-based)  
- Retry attempts  
- Errors (if any)  
- User feedback (👍 / 👎)  

---

## 🧠 Evaluation Metrics (LLM-as-a-Judge)

Each response is evaluated using an LLM-based evaluator:

| Metric       | Description                                   |
|--------------|-----------------------------------------------|
| Accuracy     | Does the response correctly reflect the data? |
| Coverage     | Does it fully answer the user’s question?     |
| Faithfulness | Is the response grounded in the data?         |
| Clarity      | Is the response easy to understand?           |
| Overall      | Overall quality score                         |

---

## 📈 How Evaluation is Used

- Identify low-quality responses for debugging  
- Improve prompt engineering iteratively  
- Enable model comparison and tuning  
- Support evaluation-driven development lifecycle  

---

## ⚙️ Logging Architecture

- Logs are stored in a **SQLite database (`logs.db`)**  
- Data is stored as structured JSON for flexibility  

### Tables:
- `logs` → interaction data  
- `feedback` → user feedback  

- Database is **auto-created at runtime** (no setup required)  

---

## 🔐 Environment Configuration (IMPORTANT)

To ensure logs persist after deployment, configure:

```bash
DB_PATH=/home/site/wwwroot/logs.db
```

### 📍 Azure Setup

1. Go to **Azure Web App**  
2. Navigate to **Settings → Environment Variables**  
3. Add:
   - **Name**: `DB_PATH`  
   - **Value**: `/home/site/wwwroot/logs.db`  
4. Save and restart the app  

---

## 🧠 Why This Matters (Logging)

Azure Web Apps use a partially **ephemeral filesystem**:

| Path        | Behavior           |
|-------------|--------------------|
| `/home/...` | ✅ Persistent       |
| Other paths | ❌ Reset on restart |

Without this configuration, logs may be lost after redeployments.

---

## 🎯 Purpose of Logging

- Monitor response quality  
- Debug SQL generation failures  
- Track LLM performance  
- Improve prompts and system behavior  
- Enable evaluation-driven development  

---

## 📦 Storage Strategy

- **Current**: SQLite (lightweight, persistent, zero setup)  

- **Future-ready for**:
  - Postgres / Cloud DB  
  - Analytics dashboards  
  - Monitoring pipelines  

---

## 🚀 Production Considerations

- Migrate from SQLite to scalable data warehouse (e.g., Snowflake, BigQuery)  
- Introduce caching layer for frequent queries to reduce latency and cost  
- Implement role-based access control and row-level security  
- Add query validation and guardrails for safe execution  
- Optimize token usage via prompt compression and response caching  

---

## 🔮 Future Enhancements

- 📊 Evaluation dashboard (metrics over time)  
- 🔍 Failure analysis (low-score queries)  
- ⚡ Real-time monitoring  
- 🤖 Automated prompt optimization  

---

## 🧩 End-to-End Ownership

This project demonstrates the full lifecycle of an AI product:
- Problem identification  
- Solution design (LLM-based architecture)  
- Implementation and deployment (Azure)  
- Evaluation and observability  
- Iterative improvement through logging and feedback  

---

## 👤 Author

**Ayush Gupta**  
AI Consultant  
