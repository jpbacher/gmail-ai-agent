from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def summarize_email(body: str) -> str:
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Summarize the following email in 2-3 concise"
                        "sentences for a daily inbox digest."
                    )
                },
                {
                    "role": "user",
                    "content": body
                }
            ],
            temperature=0.5,
            max_tokens=100
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"⚠️ Failed to summarize: {e}"
    