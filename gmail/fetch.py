from googleapiclient.discovery import build
from datetime import datetime, timezone

def fetch_today_primary_emails(creds):
    """
    Builds the Gmail API service and fetches emails from the 'Primary' inbox received today (UTC).
    Returns a list of email metadata and the service object.
    """
    service = build("gmail", "v1", credentials=creds)
    today_utc = datetime.now(timezone.utc).date()

    results = service.users().messages().list(
        userId='me',
        labelIds=['INBOX'],
        q=f'category:primary after:{today_utc}'
    ).execute()

    return results.get('messages', []), service