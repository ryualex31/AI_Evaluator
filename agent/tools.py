from agent.prompts import sql_prompt
from utils.llm import call_llm
import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "db/data.db")


def generate_sql(query, schema):
    prompt = sql_prompt(query, schema)
    sql = call_llm(prompt)
    return sql.strip().replace("```sql", "").replace("```", "")


def execute_sql(query):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute(query)

        columns = [desc[0] for desc in cursor.description]
        rows = cursor.fetchall()

        conn.close()
        return columns, rows

    except Exception as e:
        return str(e)