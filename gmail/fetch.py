from datetime import datetime, timezone
from googleapiclient.discovery import build
from utils.timestamp_tracker import load_last_run_time
from utils.logger import get_logger

logger = get_logger()


def fetch_recent_primary_emails(creds):
    """
    Fetches today's emails from the Primary category that have 
    not been processed in the last run.

    Args:
        creds: Google credentials object.

    Returns:
        Tuple: (List of new message dicts, Gmail API service object)
    """
    service = build("gmail", "v1", credentials=creds)
    last_run_ts = load_last_run_time()
    today_utc = datetime.now(timezone.utc).date()

    logger.info(f"📅 Last run timestamp: {last_run_ts}")

    response = service.users().messages().list(
        userId='me',
        labelIds=['INBOX'],
        q=f'category:primary after:{today_utc}'
    ).execute()

    message_ids = response.get('messages', [])
    logger.info(f"📥 Messages returned from Gmail API: {len(message_ids)}")
    
    new_messages = []

    for msg_meta in message_ids:
        msg_detail = service.users().messages().get(userId='me', id=msg_meta['id']).execute()
        internal_ts = int(msg_detail.get('internalDate', 0)) // 1000

        logger.debug(f"🕓 Email timestamp: {internal_ts} | Last run timestamp: {last_run_ts}")

        if internal_ts <= last_run_ts:
            logger.info("⏩ Skipping previously scanned email.")
            continue

        new_messages.append(msg_detail)

    return new_messages, service
