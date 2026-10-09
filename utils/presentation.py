"""Validate optional model output before it reaches the UI."""
import csv
import io
import math
from numbers import Real
import re


def normalize_score(value):
    if isinstance(value, str):
        match = re.fullmatch(r"([0-5])(?:/5)?", value.strip())
        return int(match.group(1)) if match else None
    return value if type(value) is int and 0 <= value <= 5 else None


def confidence_label(value):
    score = normalize_score(value)
    if score is None:
        return "unavailable"
    return "high" if score >= 4 else "medium" if score == 3 else "low"


def is_number(value):
    return isinstance(value, Real) and not isinstance(value, bool) and math.isfinite(value)


def normalize_chart(chart, columns, rows):
    if not isinstance(chart, dict) or len(rows) < 2:
        return None
    kind, x, y = chart.get("type"), chart.get("x"), chart.get("y")
    if kind not in {"line", "bar", "area", "pie"} or not isinstance(x, str) or not isinstance(y, str):
        return None
    names = {column.lower(): column for column in columns}
    x, y = names.get(x.lower()), names.get(y.lower())
    if x is None or y is None or x == y:
        return None
    index = columns.index(y)
    values = [row[index] for row in rows if row[index] is not None]
    if not values or not all(is_number(value) for value in values):
        return None
    if kind == "pie" and (len(rows) > 5 or min(values) < 0 or sum(values) <= 0):
        return None
    return {"type": kind, "x": x, "y": y}


def default_chart(columns, rows):
    if len(columns) < 2:
        return None
    for y in columns[1:]:
        chart = normalize_chart({"type": "bar", "x": columns[0], "y": y}, columns, rows)
        if chart:
            return chart
    return None


def result_csv(columns, rows):
    def safe_cell(value):
        if isinstance(value, str) and value.startswith(("=", "+", "-", "@", "\t", "\r")):
            return "'" + value
        return value
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([safe_cell(value) for value in columns])
    writer.writerows([safe_cell(value) for value in row] for row in rows)
    return output.getvalue()
