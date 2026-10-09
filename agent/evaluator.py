import json
import re

from agent.prompts import evaluation_prompt
from utils.llm import call_llm
from utils.presentation import normalize_score

METRICS = ("accuracy", "coverage", "faithfulness", "clarity", "overall")


def clean_llm_json(response):
    if not isinstance(response, str):
        return None
    try:
        match = re.search(r"\{.*\}", response, re.DOTALL)
        data = json.loads(match.group()) if match else None
        if not isinstance(data, dict):
            return None
        return {**data, **{key: normalize_score(data.get(key)) for key in METRICS}}
    except (ValueError, TypeError):
        return None


def evaluate_response(query, sql, data, insight, summary=None):
    try:
        parsed = clean_llm_json(call_llm(evaluation_prompt(query, sql, data, insight, summary)))
        if parsed:
            return parsed
    except Exception:
        pass
    return {**dict.fromkeys(METRICS), "reasoning": "Evaluation unavailable"}
