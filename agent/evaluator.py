import json
from agent.prompts import evaluation_prompt
from utils.llm import call_llm


def evaluate_response(query, sql, data, insight):
    response = call_llm(
        evaluation_prompt(query, sql, data, insight)
    )

    try:
        return json.loads(response)
    except:
        return {
            "accuracy": None,
            "coverage": None,
            "faithfulness": None,
            "clarity": None,
            "overall": None,
            "reason": "Parsing failed"
        }