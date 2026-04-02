# 📊 AI Financial Analyst

AI-powered app that lets you query financial data using natural language and get instant answers and insights.

---

## 🚀 Demo

👉 https://aicasestudy.azurewebsites.net/


### 🔐 Lightweight Login

- Email-based login for session simulation  
- Enables personalized interaction  
- Placeholder for production-grade authentication

## ✨ Features

* 💬 Natural language → SQL
* 📊 Instant data analysis
* 💡 Business insights generation

---

## 🧠 Example Queries

* Revenue trend over months
* Top products by profit
* Regional performance comparison

---

## ⚙️ Run Locally

```bash
git clone <repo-link>
cd <repo>

pip install -r requirements.txt
streamlit run app.py
```

Create `.env`:

```
AZURE_OPENAI_API_KEY=your_key
AZURE_OPENAI_ENDPOINT=your_endpoint
AZURE_OPENAI_DEPLOYMENT=gpt-4o
AZURE_OPENAI_API_VERSION=2024-02-15-preview
```

---

## 🧰 Tech Stack

* Streamlit
* Python
* SQLite
* Azure OpenAI

---

# 📝 Logging & Evaluation

The application includes a backend logging system to capture interactions and enable continuous improvement.

### 📊 What is Logged

For every user query, the system logs:

- User query  
- Generated SQL query  
- Data preview (query results)  
- Direct answer  
- Generated insights  
- Evaluation metrics  
- User feedback (👍 / 👎)  

---

### 🧠 Evaluation Metrics (LLM-as-a-Judge)

Each response is evaluated using an LLM-based evaluator to measure quality:

| Metric        | Description |
|--------------|------------|
| Accuracy     | Does the response correctly reflect the data? |
| Coverage     | Does it fully answer the user’s question? |
| Faithfulness | Is the response grounded in the data (no hallucination)? |
| Clarity      | Is the response easy to understand? |
| Overall      | Overall quality score |

---

### ⚙️ How It Works

1. After generating the answer and insights, the system calls an evaluation prompt  
2. The LLM returns structured scores (0–5)  
3. Results are parsed and stored in logs  

---

### 🎯 Purpose of Logging

- Monitor response quality  
- Identify failure patterns in SQL generation  
- Improve prompts and system behavior  
- Enable future analytics dashboards  

---

### 📦 Storage

Currently, logs are stored locally (JSON / SQLite depending on configuration).

⚠️ In production, this can be extended to:
- Cloud databases (Postgres, MongoDB)  
- Analytics pipelines  
- Monitoring dashboards  

---

### 🔮 Future Enhancements

- Evaluation dashboard (visualize metrics over time)  
- Confidence scoring for responses  
- Automatic prompt tuning using feedback  

## 👤 Author

Ayush Gupta
