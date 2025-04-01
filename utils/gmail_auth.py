from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]


def get_gmail_service(token_path="token.json"):
    """
    Loads Gmail credentials from token.json and returns an authenticated service client.
    Returns a service object that can be used to interact with the Gmail API.
    """
    creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    service = build("gmail", "v1", credentials=creds)
    return service