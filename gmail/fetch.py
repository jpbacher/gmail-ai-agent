from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from datetime import datetime, timezone

def fetch_today_primary_emails(creds):
    """
    Fetches emails from the Gmail inbox labeled 'Primary' that were received today (UTC).
    Returns a list of email message metadata.
    """
    service = build("gmail", "v1", credentials=creds)

    # Get today’s UTC date for filtering
    today_utc = datetime.now(timezone.utc).date()

    results = service.users().messages().list(
        userId='me',
        labelIds=['INBOX'],
        q=f'category:primary after:{today_utc}'
    ).execute()

    return results.get('messages', []), service