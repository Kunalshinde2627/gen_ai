
import os
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"


def ask_llm(system_prompt, user_message, temperature=0.2):
    """Send a system prompt and a user message to Groq."""
    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        raise RuntimeError("GROQ_API_KEY is missing. Add it to your .env file.")

    model = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

    response = requests.post(
        GROQ_URL,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json={
            "model": model,
            "temperature": temperature,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
        },
        timeout=60,
    )

    if response.status_code != 200:
        raise RuntimeError(
            f"Groq error {response.status_code}: {response.text[:300]}"
        )

    return response.json()["choices"][0]["message"]["content"]
