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


def should_upload_summary(subject: str, sender: str, body: str) -> bool:
    """
    Determines whether a summary should be uploaded to S3.
    Newsletter-like emails are uploaded; job alerts are excluded.
    Args:
        subject (str): Email subject
        sender (str): Sender email
        body (str): Full email body
    Returns:
        bool: True if summary should be saved to S3
    """
    sender_lower = sender.lower()
    subject_lower = subject.lower()
    body_lower = body.lower()

    job_alert_keywords = [
        "job alert", "job opportunity", "job opening",
        "career opportunity", "job posting", "job vacancy",
        "job listing", "job application", "job search",
        "job offer", "job position", "job description",
        "job details", "job requirements",
        "job responsibilities", "job duties", "job qualifications",
        "job skills", "job experience", "job match", "recommended job",
        "job recommendation", "job suggestion", "job fit",
        "job fit", "linkedin job alerts", "indeed", "ziprecruiter",
        "monster", "glassdoor", "careerbuilder",
        "glassdor", "lensa 24", "jobcase",
        "jobscan", "simplyhired", "workable",
    ]

    if any(keyword in sender_lower for keyword in job_alert_keywords):
        return False
    if any(keyword in subject_lower for keyword in job_alert_keywords):
        return False
    if any(keyword in body_lower for keyword in job_alert_keywords):
        return False

    return True
