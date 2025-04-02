from datetime import datetime
from gmail_auth import authenticate_gmail
from gmail.fetch import fetch_emails_since
from gmail.parser import extract_plain_text_body, extract_headers
from gmail.filter import is_likely_automated_email
from agent.responder import generate_gpt_reply
from utils.logger import get_logger
from utils.timestamp_tracker import load_last_run_time, save_last_run_time
from utils.summary_tracker import create_summary, update_summary, save_summary


logger = get_logger()


def main():
    creds = authenticate_gmail()
    
    # Load the timestamp of the last successful run
    last_run_timestamp = load_last_run_time()
    logger.info(f"📅 Last run timestamp: {last_run_timestamp}")

    messages, _ = fetch_emails_since(creds, last_run_timestamp)

    summary = create_summary()

    skipped_count = 0
    processed_count = 0

    for msg in messages:
        payload = msg.get("payload", {})
        subject, date, sender, headers = extract_headers(payload)
        body = extract_plain_text_body(payload)
        
        is_automated, reason = is_likely_automated_email(
            headers, subject, body)
        if is_automated:
            logger.info(f"⛔ Skipping email from: {sender} | Subject: {subject} — Reason: {reason}")
            update_summary(summary, "skipped", subject)
            skipped_count += 1
            continue

        if body:
            logger.info(f"✉️ Generating response for: {subject}")
            processed_count += 1
            response = generate_gpt_reply(body)
            print(f"\nSuggested Response for '{subject}':\n{response}")
            update_summary(summary,"processed", subject)
        else:
            logger.warning(f"⚠️ No body found for email: {subject}")

    # Save current timestamp after successful processing
    save_last_run_time(int(datetime.now(datetime.timezone.utc.timestamp())))
    save_summary(summary)
    logger.info(f"Summary — Skipped: {skipped_count}, Responded: {processed_count}")
    logger.info("✅ Timestamp updated after run.")
    logger.info("✅ Summary written to logs/summary.json")


if __name__ == "__main__":
    main()
