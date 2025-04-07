import os
from google.oauth2.credentials import Credentials
from google.auth.exceptions import RefreshError
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]


def authenticate_gmail():
    """
    Authenticates the user with Gmail API and returns credentials.
    If the token is expired or revoked, it triggers re-authentication.
    """
    creds = None

    if os.path.exists("token.json"):
        try:
            creds = Credentials.from_authorized_user_file("token.json", SCOPES)
            # Attempt to refresh token to validate it
            _ = creds.valid  # this line could also trigger validation in some flows
        except RefreshError:
            print("⚠️ Token expired or revoked. Re-authenticating...")
            creds = None  # Trigger re-authentication below

    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file("gmail-credentials.json", SCOPES)
        creds = flow.run_local_server(port=0)

        # Save new token
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    return creds
