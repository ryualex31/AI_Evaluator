from functools import lru_cache
import os


@lru_cache(maxsize=1)
def _get_client():
    from dotenv import load_dotenv
    from openai import AzureOpenAI
    load_dotenv()
    required = ("AZURE_OPENAI_API_KEY", "AZURE_OPENAI_ENDPOINT", "AZURE_OPENAI_DEPLOYMENT")
    if any(not os.getenv(key) for key in required):
        raise RuntimeError("The analysis provider is not configured.")
    return AzureOpenAI(
        api_key=os.environ["AZURE_OPENAI_API_KEY"],
        api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview"),
        azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
        timeout=30.0,
        max_retries=2,
    )


def call_llm(prompt, temperature=0):
    client = _get_client()
    response = client.chat.completions.create(
        model=os.environ["AZURE_OPENAI_DEPLOYMENT"],
        messages=[
            {"role": "system", "content": "You are a precise and reliable AI assistant."},
            {"role": "user", "content": prompt},
        ],
        temperature=temperature,
    )
    content = response.choices[0].message.content
    if not content or not content.strip():
        raise RuntimeError("The analysis provider returned an empty response.")
    return content.strip()
