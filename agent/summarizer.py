import os
import logging
from openai import OpenAI
from dotenv import load_dotenv


load_dotenv()
logger = logging.getLogger(__name__)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def summarize_email(email_body: str) -> str:
    """
    Uses OpenAI to generate a concise summary of an email.
    
    Args:
        email_body (str): Full email content to summarize.
        
    Returns:
        str: GPT-generated summary.
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a helpful assistant that summarizes emails in 1-3 sentences."
                        "Highlight the key point or action if present."
                    )
                },
                {
                    "role": "user",
                    "content": email_body
                }
            ],
            temperature=0.5,
            max_tokens=100
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logger.exception(f"❌ Failed to summarize email: {e}")
        return "⚠️ Could not generate summary."
    