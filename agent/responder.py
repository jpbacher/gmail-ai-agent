import os
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


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
                        "You are a helpful assistant who drafts brief and professional email responses. "
                        "Only generate a reply if it makes sense to respond based on the content provided. "
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
    except Exception as e:
        print(f"❌ Error generating GPT response: {e}")
        return "⚠️ Unable to generate a response at this time."