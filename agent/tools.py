import sqlite3
from utils.llm import call_llm
from agent.prompts import generate_sql_prompt


def generate_sql(query, schema):
    prompt = generate_sql_prompt(query, schema)
    return call_llm(prompt).strip()


def execute_sql(query):
    conn = sqlite3.connect("db/data.db")
    cursor = conn.cursor()

    try:
        cursor.execute(query)
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        return columns, rows
    except Exception as e:
        return str(e)
