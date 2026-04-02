import json
import re
from agent.prompts import evaluation_prompt
from utils.llm import call_llm


def clean_llm_json(response: str):
    try:
        # Remove markdown
        response = re.sub(r"```json|```", "", response).strip()

        # Extract JSON
        match = re.search(r"\{.*\}", response, re.DOTALL)
        if not match:
            return None

        data = json.loads(match.group())

        # Normalize keys + values
        for key in ["accuracy", "coverage", "faithfulness", "clarity", "overall"]:
            val = data.get(key)

            # Handle "4/5" case
            if isinstance(val, str) and "/" in val:
                val = val.split("/")[0]

            try:
                data[key] = int(val)
            except:
                data[key] = None

        return data

    except Exception as e:
        print("Parsing error:", e)
        print("Raw response:", response)
        return None


def evaluate_response(query, sql, data, insight):

    response = call_llm(
        evaluation_prompt(query, sql, data, insight)
    )

    print("\n=== EVALUATOR RAW ===\n", response)

    if not response or response.strip() == "":
        return {
            "accuracy": None,
            "coverage": None,
            "faithfulness": None,
            "clarity": None,
            "overall": None,
            "reasoning": "Empty response"
        }

    parsed = clean_llm_json(response)

    if parsed:
        return parsed

    return {
        "accuracy": None,
        "coverage": None,
        "faithfulness": None,
        "clarity": None,
        "overall": None,
        "reasoning": f"Parsing failed. Raw: {response}"
    }