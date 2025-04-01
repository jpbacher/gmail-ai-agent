import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

def authenticate_gmail():
    """
    Authenticates the user with Gmail API and returns credentials.
    """
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    else:
        flow = InstalledAppFlow.from_client_secrets_file("gmail-credentials.json", SCOPES)
        creds = flow.run_local_server(port=0)

        # Save the credentials for future use
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    return creds