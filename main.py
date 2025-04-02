from gmail_auth import authenticate_gmail
from gmail.fetch import fetch_today_primary_emails
from gmail.parser import extract_plain_text_body, extract_headers
from gmail.filter import is_likely_automated_email
from agent.responder import generate_gpt_reply
from utils.logger import get_logger

logger = get_logger()


def main():
    creds = authenticate_gmail()
    emails, service = fetch_today_primary_emails(creds)

    if not emails:
        logger.info("No new primary emails today.")
        return

    for msg in emails:
        msg_detail = service.users().messages().get(userId='me', id=msg['id']).execute()
        payload = msg_detail.get("payload", {})

        subject, date, sender, headers = extract_headers(payload)
        body = extract_plain_text_body(payload)

        is_automated, reason = is_likely_automated_email(headers, subject, body)
        if is_automated:
            logger.info(f"⛔ Skipping email from: {sender} | Subject: {subject} — Reason: {reason}")
            continue

        if body:
            logger.info(f"✉️ Generating response for: {subject}")
            response = generate_gpt_reply(body)
            print(f"\nSuggested Response for '{subject}':\n{response}")
        else:
            logger.warning(f"⚠️ No body found for email: {subject}")


if __name__ == "__main__":
    main()