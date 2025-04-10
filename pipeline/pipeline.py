import re
from gmail_auth import authenticate_gmail
from gmail.fetch import fetch_recent_primary_emails
from gmail.parser import extract_headers, extract_plain_text_body
from gmail.filter import is_likely_automated_email
from agent.responder import generate_gpt_reply
from agent.summarizer import summarize_email
from utils.timestamp_tracker import load_last_run_time
from utils.logger import get_logger

logger = get_logger()


def extract_email_address(from_header: str) -> str:
    """Extracts email from 'From' header like 'John Doe <john@example.com>'."""
    match = re.search(r'<(.+?)>', from_header)
    if match:
        return match.group(1)
    return from_header


def get_emails_for_ui():
    creds = authenticate_gmail()
    messages, service = fetch_recent_primary_emails(
        creds
    )

    if not messages:
        return [], [], service

    last_run_ts = load_last_run_time()
    reply_emails = []
    summary_emails = []

    for msg_meta in messages:
        msg_detail = service.users().messages().get(
            userId="me", id=msg_meta["id"]).execute()
        internal_ts = int(msg_detail.get("internalDate", 0)) // 1000
        if internal_ts <= last_run_ts:
            continue

        payload = msg_detail.get("payload", {})
        body = extract_plain_text_body(payload)
        subject, date, sender, headers = extract_headers(payload)

        if not body or is_likely_automated_email(headers, subject, body)[0]:
            continue
        
        to_email = extract_email_address(sender)
        
        # Use GPT to decide if it's a reply or a summary case
        reply = generate_gpt_reply(body)
        if (reply.lower().startswith("⚠️ unable to generate") or
                "no response needed"):
            # If no useful reply, generate a summary instead
            summary = summarize_email(body)
            summary_emails.append({
                "subject": subject,
                "sender": sender,
                "body": body[:500] + "...",
                "summary": summary
            })
        else:
            reply_emails.append({
                "subject": subject,
                "sender": sender,
                "to_email": to_email,
                "body": body[:500] + "...",
                "suggested_response": reply,
                "message_id": msg_detail.get("id"),
                "thread_id": msg_detail.get("threadId")
            })

    return reply_emails, summary_emails, service
