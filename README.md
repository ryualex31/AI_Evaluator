# 📊 AI Financial Analyst

AI-powered application that allows users to query financial data using natural language and receive **accurate answers, SQL-backed insights, and business intelligence** instantly.

---

## 🚀 Demo

👉 https://aicasestudy.azurewebsites.net/

---

## 🔐 Lightweight Login

* Email-based login for session simulation
* Enables personalized interaction
* Placeholder for production-grade authentication

---

## ✨ Features

* 💬 Natural Language → SQL conversion
* 📊 Instant data retrieval & visualization
* 💡 AI-generated business insights
* 🔁 Automatic SQL correction (retry mechanism)
* 🧠 LLM-based response evaluation
* 📝 Persistent logging for observability

---

## 🧠 Example Queries

* Revenue trend over months
* Top products by profit
* Regional performance comparison
* Monthly growth rate analysis
* Profit margin by category

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

* **Frontend**: Streamlit
* **Backend**: Python
* **LLM**: Azure OpenAI
* **Database**: SQLite
* **Architecture**: LLM-powered agent pipeline

---

# 🧠 System Architecture

The system follows a modular **LLM-agent pipeline**:

1. **Intent Classification** → Determines if query is financial
2. **SQL Generation** → Converts NL → SQL using LLM
3. **Execution Engine** → Runs SQL on structured data
4. **Retry Logic** → Fixes invalid SQL automatically
5. **Response Generation** → Direct answer + insights
6. **Evaluation Layer** → LLM-as-a-judge scoring
7. **Logging Layer** → Stores all interactions

---

# 📝 Logging & Evaluation

The application includes a **production-ready SQLite-based logging system** to capture interactions, enable evaluation, and support continuous improvement.

---

## 📊 What is Logged

For every user query, the system captures:

* User query
* Intent classification
* Generated SQL query
* SQL prompt used
* Query results (preview)
* Direct answer
* Generated insights
* Evaluation metrics (LLM-based)
* Retry attempts
* Errors (if any)
* User feedback (👍 / 👎)

---

## 🧠 Evaluation Metrics (LLM-as-a-Judge)

Each response is evaluated using an LLM-based evaluator:

| Metric       | Description                                   |
| ------------ | --------------------------------------------- |
| Accuracy     | Does the response correctly reflect the data? |
| Coverage     | Does it fully answer the user’s question?     |
| Faithfulness | Is the response grounded in the data?         |
| Clarity      | Is the response easy to understand?           |
| Overall      | Overall quality score                         |

---

## ⚙️ Logging Architecture

* Logs are stored in a **SQLite database (`logs.db`)**

* Data is stored as structured JSON for flexibility

* Tables:

  * `logs` → interaction data
  * `feedback` → user feedback

* Database is **auto-created at runtime** (no setup required)

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

   * **Name**: `DB_PATH`
   * **Value**: `/home/site/wwwroot/logs.db`
4. Save and restart the app

---

## 🧠 Why This Matters

Azure Web Apps use a partially **ephemeral filesystem**:

| Path        | Behavior           |
| ----------- | ------------------ |
| `/home/...` | ✅ Persistent       |
| Other paths | ❌ Reset on restart |

Without this configuration, logs may be lost after redeployments.

---

## 🎯 Purpose of Logging

* Monitor response quality
* Debug SQL generation failures
* Track LLM performance
* Improve prompts and system behavior
* Enable evaluation-driven development

---

## 📦 Storage Strategy

* **Current**: SQLite (lightweight, persistent, zero setup)
* **Future-ready for**:

  * Postgres / Cloud DB
  * Analytics dashboards
  * Monitoring pipelines

---

## 🔮 Future Enhancements

* 📊 Evaluation dashboard (metrics over time)
* 🔍 Failure analysis (low-score queries)
* ⚡ Real-time monitoring
* 🤖 Automated prompt optimization

---

## 👤 Author

**Ayush Gupta**
AI Consultant
