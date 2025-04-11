import os
from openai import OpenAI
from dotenv import load_dotenv
from utils.logger import get_logger

# Load environment variables from .env
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

logger = get_logger(__name__)


def generate_gpt_reply(email_body):
    """
    Generates a GPT-based reply suggestion for a given email body using OpenAI's API.

    Args:
        email_body (str): The plain text content of the incoming email.

    Returns:
        str: A suggested response based on the content of the email.
    """
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a helpful assistant who drafts brief and "
                        "professional email responses. "
                        "Sign off every message with 'Best, Josh Bacher'. "
                        "Only generate a reply if it makes sense to respond "
                        "based on the content provided. "
                        "Avoid generic greetings like 'How can I help you?'."
                    )
                },
                {
                    "role": "user",
                    "content": email_body
                }
            ],
            temperature=0.5,
            max_tokens=150
        )
        return response.choices[0].message.content.strip()
    except Exception:
        logger.exception("❌ Error generating GPT response")
        return "⚠️ Unable to generate a response at this time."
    

def email_requires_response(email_body):
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a smart email classifier. "
                        "Only respond with 'yes' if the email clearly needs a "
                        "reply from the recipient. "
                        "Respond with 'no' if it is a newsletter, job alert, "
                        "notification, or no reply is needed."
                    )
                },
                {"role": "user", "content": f"Does this email require a reply?\\n\\n{email_body}"}
            ],
            temperature=0,
            max_tokens=3
        )
        answer = response.choices[0].message.content.strip().lower()
        return answer.startswith("y")
    except Exception:
        logger.exception("❌ Error during email response classification.")
        return False
