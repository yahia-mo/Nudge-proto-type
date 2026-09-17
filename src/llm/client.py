import os

from openai import OpenAI

DEFAULT_MODEL = "qwen/qwen3.8-27b"


def get_llm_client(api_key: str | None = None) -> OpenAI:
    key = api_key or os.getenv("GROQ_API_KEY")
    if not key:
        raise ValueError("GROQ_API_KEY is not configured in the environment or request payload.")
    return OpenAI(base_url="https://api.groq.com/openai/v1", api_key=key)