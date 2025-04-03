def fetch_recent_primary_emails(service, max_results=21):
    """
    Fetch recent 'Primary' labeled emails. We'll filter by timestamp later.
    """
    results = service.users().messages().list(
        userId='me',
        labelIds=['INBOX'],
        q='category:primary',
        maxResults=max_results  
    ).execute()

    messages = results.get("messages", [])
    return messages
