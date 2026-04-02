import json
import re
from agent.prompts import evaluation_prompt
from utils.llm import call_llm


def extract_json(text):
    try:
        # Extract JSON block using regex
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            return json.loads(match.group())
    except:
        pass
    return None


def evaluate_response(query, sql, data, insight):
    response = call_llm(
        evaluation_prompt(query, sql, data, insight)
    )

    parsed = extract_json(response)

    if parsed:
        return parsed

    return {
        "accuracy": None,
        "coverage": None,
        "faithfulness": None,
        "clarity": None,
        "overall": None,
        "reason": f"Parsing failed. Raw output: {response}"
    }