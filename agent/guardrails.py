from agent.prompts import intent_prompt
from utils.llm import call_llm


def classify_intent(query):
    return call_llm(intent_prompt(query)).strip().upper()