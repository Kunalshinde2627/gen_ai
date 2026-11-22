import os
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

TOKEN_COUNTER = {"total": 0}


def reset_tokens():
    """Call at the start of a request."""
    TOKEN_COUNTER["total"] = 0


def get_tokens():
    """Tokens used by all LLM calls since reset_tokens()."""
    return TOKEN_COUNTER["total"]


def ask_llm(system_prompt, user_message, temperature=0.2):
    """Send a system prompt and user message to Groq."""

    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        raise RuntimeError(
            "GROQ_API_KEY is missing. Add it to your .env file."
        )

    model = os.getenv(
        "GROQ_MODEL",
        "llama-3.3-70b-versatile"
    )

    payload = {
        "model": model,
        "temperature": temperature,
        "messages": [
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": user_message
            }
        ]
    }

    response = requests.post(
        GROQ_URL,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        },
        json=payload,
        timeout=60
    )

    if response.status_code != 200:
        raise RuntimeError(
            f"Groq error {response.status_code}: "
            f"{response.text[:500]}"
        )

    data = response.json()

    # Count the tokens used by this call
    TOKEN_COUNTER["total"] += data.get("usage", {}).get("total_tokens", 0)

    message = data["choices"][0]["message"]

    # Check if the model returned normal text
    content = message.get("content")

    if content:
        return content

    # Tool calls are not expected in this application
    if message.get("tool_calls"):
        raise RuntimeError(
            "Groq returned an unexpected tool call. "
            "Expected a JSON text response instead."
        )

    raise RuntimeError(
        "Groq returned an empty response."
    )