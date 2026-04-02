def to_markdown_table(columns, rows, max_rows=10):
    rows = rows[:max_rows]

    header = "| " + " | ".join(columns) + " |"
    separator = "| " + " | ".join(["---"] * len(columns)) + " |"

    body = "\n".join([
        "| " + " | ".join(str(cell) for cell in row) + " |"
        for row in rows
    ])

    return f"{header}\n{separator}\n{body}"