from contextlib import closing
from pathlib import Path
import sqlite3
import time

from agent.prompts import sql_prompt
from utils.llm import call_llm

DB_PATH = str(Path(__file__).resolve().parents[1] / "db" / "data.db")
MAX_RESULT_ROWS = 200
MAX_QUERY_CHARS = 10_000
QUERY_TIMEOUT_SECONDS = 2.0


def generate_sql(query, schema):
    return call_llm(sql_prompt(query, schema)).strip().replace("```sql", "").replace("```", "")


def _authorize(action, table, detail, database, source):
    if action in (sqlite3.SQLITE_SELECT, sqlite3.SQLITE_RECURSIVE):
        return sqlite3.SQLITE_OK
    if action == sqlite3.SQLITE_READ and table == "financials" and database == "main":
        return sqlite3.SQLITE_OK
    if action == sqlite3.SQLITE_FUNCTION and (detail or "").lower() not in {
        "load_extension", "readfile", "writefile",
    }:
        return sqlite3.SQLITE_OK
    return sqlite3.SQLITE_DENY


def execute_sql(query):
    """Return a complete, bounded result from the read-only financials database."""
    if not isinstance(query, str) or not query.strip() or len(query) > MAX_QUERY_CHARS:
        return "Provide a nonempty query within the supported size."
    try:
        uri = Path(DB_PATH).resolve().as_uri() + "?mode=ro"
        with closing(sqlite3.connect(uri, uri=True, timeout=QUERY_TIMEOUT_SECONDS)) as connection:
            connection.setlimit(sqlite3.SQLITE_LIMIT_LENGTH, 100_000)
            connection.set_authorizer(_authorize)
            deadline = time.monotonic() + QUERY_TIMEOUT_SECONDS
            connection.set_progress_handler(lambda: int(time.monotonic() >= deadline), 1000)
            cursor = connection.execute(query)
            if cursor.description is None:
                return "Only read-only financial queries are supported."
            columns = [item[0] for item in cursor.description]
            if len(set(columns)) != len(columns):
                return "Give every result column a distinct alias."
            rows = cursor.fetchmany(MAX_RESULT_ROWS + 1)
            if len(rows) > MAX_RESULT_ROWS:
                return "This result is too large to summarize reliably. Narrow the date range or grouping."
            return columns, rows
    except sqlite3.Error as error:
        return str(error)
