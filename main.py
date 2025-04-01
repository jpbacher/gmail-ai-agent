from gmail.auth import get_gmail_service
from gmail.fetch import fetch_today_primary_emails
from gmail.parser import extract_plain_text_body
from gmail.filter import is_likely_newsletter
from agent.responder import generate_gpt_reply 
from utils.logger import get_logger

logger = get_logger()

def main():
    service = get_gmail_service()
    emails = fetch_today_primary_emails(service)

    if not emails:
        logger.info("No new primary emails found today.")
        return

    logger.info(f"Found {len(emails)} new email(s) in Primary today.")
    for msg in emails:
        subject = msg.get("subject", "No Subject")
        sender = msg.get("from", "Unknown Sender")
        headers = msg.get("headers", [])
        body = extract_plain_text_body(msg)  # ✅ fixed: only 1 argument needed now

        if is_likely_newsletter(headers, subject, body):
            logger.info(f"⛔ Skipping likely newsletter or job alert from: {sender} | Subject: {subject}")
            continue

        logger.info(f"📩 Processing email from {sender} | Subject: {subject}")
        logger.info("📨 Email preview:")
        logger.info(body[:300] + "..." if body else "[No body]")

        logger.info("🤖 Generating GPT-based response suggestion...")
        suggestion = generate_gpt_reply(body)

        if suggestion:
            logger.info("💡 Suggested Response:")
            logger.info(suggestion)
            logger.info("=" * 60)
        else:
            logger.warning("⚠️ No suggestion generated.")

if __name__ == "__main__":
    main()