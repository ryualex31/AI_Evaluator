import csv
import io
import json
import os
from pathlib import Path
import sqlite3
import tempfile
import unittest
from unittest.mock import patch

# Tests must never read credentials or write the application's production logs.
_logs = tempfile.TemporaryDirectory()
os.environ["DB_PATH"] = str(Path(_logs.name) / "logs.db")

from agent import evaluator, orchestrator, tools
from utils.presentation import confidence_label, default_chart, normalize_chart, result_csv


class SQLSafetyTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.path = Path(self.temp.name) / "data.db"
        with sqlite3.connect(self.path) as conn:
            conn.execute("CREATE TABLE financials(month TEXT, revenue REAL)")
            conn.executemany("INSERT INTO financials VALUES (?, ?)", [("January", 100), ("December", 200)])
            conn.execute("CREATE TABLE secret(value TEXT)")
        self.database = patch.object(tools, "DB_PATH", str(self.path))
        self.database.start()

    def tearDown(self):
        self.database.stop()
        self.temp.cleanup()

    def test_aggregate_and_cte_remain_supported(self):
        self.assertEqual(tools.execute_sql("SELECT SUM(revenue) AS total FROM financials"), (["total"], [(300.0,)]))
        self.assertEqual(tools.execute_sql("WITH totals AS (SELECT SUM(revenue) AS total FROM financials) SELECT total FROM totals"), (["total"], [(300.0,)]))

    def test_mutations_and_other_tables_are_denied_and_data_survives(self):
        queries = ["DROP TABLE financials", "DELETE FROM financials RETURNING revenue",
                   "UPDATE financials SET revenue=0 RETURNING revenue",
                   "INSERT INTO financials VALUES ('bad', 0)", "PRAGMA user_version=99",
                   "ATTACH DATABASE ':memory:' AS attached", "SELECT * FROM secret",
                   "SELECT load_extension('malicious')", "SELECT * FROM sqlite_master"]
        for query in queries:
            with self.subTest(query=query):
                self.assertIsInstance(tools.execute_sql(query), str)
        with sqlite3.connect(self.path) as conn:
            self.assertEqual(conn.execute("SELECT SUM(revenue) FROM financials").fetchone()[0], 300)
            self.assertEqual(conn.execute("PRAGMA user_version").fetchone()[0], 0)

    def test_oversized_results_are_rejected_instead_of_truncated(self):
        with sqlite3.connect(self.path) as conn:
            conn.executemany("INSERT INTO financials VALUES (?, ?)", [("Extra", 1)] * tools.MAX_RESULT_ROWS)
        self.assertIn("too large", tools.execute_sql("SELECT * FROM financials"))

    def test_expensive_queries_are_interrupted(self):
        with patch.object(tools, "QUERY_TIMEOUT_SECONDS", 0.002):
            result = tools.execute_sql("WITH RECURSIVE n(x) AS (VALUES(1) UNION ALL SELECT x+1 FROM n WHERE x<100000000) SELECT SUM(x) AS total FROM n")
        self.assertIn("interrupted", result)

    def test_missing_database_is_not_created(self):
        missing = Path(self.temp.name) / "missing.db"
        with patch.object(tools, "DB_PATH", str(missing)):
            self.assertIsInstance(tools.execute_sql("SELECT 1"), str)
        self.assertFalse(missing.exists())

    def test_oversized_sql_values_are_rejected_before_allocation(self):
        self.assertIsInstance(tools.execute_sql("SELECT length(zeroblob(100001)) AS size"), str)

    def test_duplicate_aliases_and_multiple_statements_are_rejected(self):
        self.assertIn("distinct alias", tools.execute_sql("SELECT revenue, revenue FROM financials"))
        self.assertIsInstance(tools.execute_sql("SELECT 1; DELETE FROM financials"), str)


class PresentationTests(unittest.TestCase):
    def test_invalid_scores_have_unavailable_confidence(self):
        for score in [None, True, 9, -1, 4.5, "unknown", {}, []]:
            self.assertEqual(confidence_label(score), "unavailable")
        self.assertEqual(confidence_label("4/5"), "high")
        self.assertEqual(confidence_label(3), "medium")
        self.assertEqual(confidence_label(0), "low")

    def test_scalar_and_text_results_do_not_create_charts(self):
        self.assertIsNone(default_chart(["total"], [(123,)]))
        self.assertIsNone(default_chart(["region", "name"], [("East", "A"), ("West", "B")]))
        self.assertIsNone(default_chart(["region", "total"], [("East", 123)]))

    def test_charts_validate_the_selected_measure_and_preserve_type(self):
        columns, rows = ["month", "notes", "profit"], [("Jan", "good", 12), ("Feb", "good", 15)]
        self.assertEqual(normalize_chart({"type": "line", "x": "Month", "y": "Profit"}, columns, rows),
                         {"type": "line", "x": "month", "y": "profit"})
        self.assertEqual(default_chart(columns, rows)["y"], "profit")
        for chart in [{"type": "bar", "x": "month", "y": "missing"},
                      {"type": "bar", "x": "month", "y": "notes"},
                      {"type": "html", "x": "month", "y": "profit"}]:
            self.assertIsNone(normalize_chart(chart, columns, rows))
        self.assertIsNone(normalize_chart({"type": "pie", "x": "month", "y": "profit"},
                                          columns, [("Jan", "", -1), ("Feb", "", 2)]))

    def test_csv_quotes_cells_and_neutralizes_formulas_without_changing_numbers(self):
        output = result_csv(["name", "value"], [('=SUM(1,2)', -5), ('comma,quote"', 2)])
        self.assertEqual(list(csv.reader(io.StringIO(output))), [["name", "value"], ["'=SUM(1,2)", "-5"], ['comma,quote"', "2"]])

    def test_malformed_evaluator_output_is_normalized(self):
        self.assertIsNone(evaluator.clean_llm_json("not JSON"))
        self.assertIsNone(evaluator.clean_llm_json("[]"))
        parsed = evaluator.clean_llm_json('{"overall": "4/5", "accuracy": true, "coverage": 99}')
        self.assertEqual(parsed["overall"], 4)
        self.assertIsNone(parsed["accuracy"])
        self.assertIsNone(parsed["coverage"])
        with patch.object(evaluator, "call_llm", side_effect=RuntimeError("provider failed")):
            self.assertIsNone(evaluator.evaluate_response("q", "sql", {}, None)["overall"])


class PipelineTests(unittest.TestCase):
    def test_all_twelve_months_reach_summary_insight_chart_and_evaluation(self):
        rows = [(f"Month-{i:02}", i * 10) for i in range(1, 13)]
        prompts = []
        def llm(prompt):
            prompts.append(prompt)
            return '{"type": "line", "x": "month", "y": "revenue"}' if len(prompts) == 3 else "Full year answer"
        with patch.object(orchestrator, "classify_intent", return_value="FINANCE_QUERY"), \
             patch.object(orchestrator, "generate_sql", return_value="SELECT month, revenue FROM financials"), \
             patch.object(orchestrator, "execute_sql", return_value=(["month", "revenue"], rows)), \
             patch.object(orchestrator, "call_llm", side_effect=llm), \
             patch.object(orchestrator, "evaluate_response", return_value={"overall": 4}) as evaluate, \
             patch.object(orchestrator, "log_interaction"):
            output = orchestrator.run_agent("Compare the monthly revenue trend", "schema")
        self.assertEqual(output["rows"], rows)
        self.assertEqual(output["chart"], {"type": "line", "x": "month", "y": "revenue"})
        self.assertIn("Month-12", prompts[0])
        self.assertIn("Month-12", prompts[1])
        self.assertIn("Month-12", prompts[2])
        self.assertEqual(evaluate.call_args.args[2]["rows"], rows)
        self.assertEqual(evaluate.call_args.kwargs["summary"], output["summary"])

    def test_provider_failures_return_a_safe_error(self):
        with patch.object(orchestrator, "classify_intent", side_effect=RuntimeError("secret endpoint")):
            output = orchestrator.run_agent("query", "schema")
        self.assertIn("unavailable", output["error"])
        self.assertNotIn("secret endpoint", output["error"])

    def test_sql_failure_stops_after_bounded_retries(self):
        with patch.object(orchestrator, "classify_intent", return_value="FINANCE_QUERY"), \
             patch.object(orchestrator, "generate_sql", return_value="DELETE FROM financials"), \
             patch.object(orchestrator, "execute_sql", return_value="denied") as execute, \
             patch.object(orchestrator, "call_llm", return_value="DELETE FROM financials"), \
             patch.object(orchestrator, "log_interaction"):
            output = orchestrator.run_agent("delete everything", "schema")
        self.assertEqual(execute.call_count, 3)
        self.assertIn("error", output)

    def test_evaluator_prompt_contains_the_displayed_answer(self):
        with patch.object(evaluator, "call_llm", return_value=json.dumps({"overall": 5})) as llm:
            evaluator.evaluate_response("query", "SQL", {"rows": [(12,)]}, "insight", summary="Revenue was 12.")
        self.assertIn("Displayed answer: Revenue was 12.", llm.call_args.args[0])


class StreamlitTests(unittest.TestCase):
    def app(self):
        from streamlit.testing.v1 import AppTest
        app = AppTest.from_file(str(Path(__file__).resolve().parents[1] / "app.py"), default_timeout=15)
        app.session_state["authenticated"] = True
        app.session_state["user_email"] = "test@example.com"
        return app

    def test_scalar_result_and_unavailable_evaluation_render(self):
        app = self.app()
        app.session_state["messages"] = [{"id": "scalar", "role": "assistant", "query": "total", "summary": "Total 123",
                                          "rows": [(123,)], "columns": ["total"], "evaluation": {"overall": None},
                                          "sql_query": "SELECT SUM(revenue) AS total FROM financials"}]
        app.run()
        self.assertEqual(len(app.exception), 0)
        self.assertEqual(app.metric[0].value, "123.00")
        self.assertEqual(app.info[0].value, "Confidence evaluation unavailable")

    def test_provider_failure_releases_processing_state(self):
        app = self.app()
        app.session_state["run_query"] = "total revenue"
        app.session_state["is_processing"] = True
        with patch.object(orchestrator, "run_agent", side_effect=RuntimeError("provider unavailable")):
            app.run()
        self.assertEqual(len(app.exception), 0)
        self.assertFalse(app.session_state["is_processing"])
        self.assertIsNone(app.session_state["run_query"])
        self.assertIn("unavailable", app.session_state["messages"][-1]["summary"])
        self.assertFalse(app.chat_input[0].disabled)


if __name__ == "__main__":
    unittest.main()
