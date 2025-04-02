from googleapiclient.discovery import build


def fetch_today_primary_emails(creds, since_timestamp):
    """
    Fetch emails from the Gmail inbox labeled 'Primary' 
    received after the given Unix timestamp.
    """
    service = build("gmail", "v1", credentials=creds)

    results = service.users().messages().list(
        userId='me',
        labelIds=['INBOX'],
        q=f'category:primary after:{since_timestamp}'
    ).execute()

    return results.get('messages', []), service
