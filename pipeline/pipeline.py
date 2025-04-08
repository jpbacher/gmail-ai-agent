from gmail_auth import authenticate_gmail
from gmail.fetch import fetch_recent_primary_emails
from gmail.parser import extract_headers, extract_plain_text_body
from gmail.filter import is_likely_automated_email
from agent.responder import generate_gpt_reply
from utils.timestamp_tracker import load_last_run_time
from utils.logger import get_logger

logger = get_logger()


def get_emails_for_ui():
    creds = authenticate_gmail()
    messages, service = fetch_recent_primary_emails(creds)

    if not messages:
        return []

    last_run_ts = load_last_run_time()
    email_samples = []

    for msg_meta in messages:
        msg_detail = service.users().messages().get(userId="me", id=msg_meta["id"]).execute()
        internal_ts = int(msg_detail.get("internalDate", 0)) // 1000
        if internal_ts <= last_run_ts:
            continue

        payload = msg_detail.get("payload", {})
        body = extract_plain_text_body(payload)
        subject, date, sender, headers = extract_headers(payload)

        if not body or is_likely_automated_email(headers, subject, body)[0]:
            continue

        gpt_reply = generate_gpt_reply(body)

        email_samples.append({
            "subject": subject,
            "sender": sender,
            "body": body[:500] + "...",  # trim preview
            "suggested_response": gpt_reply
        })

    return email_samples
