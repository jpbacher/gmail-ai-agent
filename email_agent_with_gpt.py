import os
import base64
from openai import OpenAI
from datetime import datetime, timezone
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Load Gmail credentials
creds = Credentials.from_authorized_user_file(
    "token.json",
    [
        "https://www.googleapis.com/auth/gmail.readonly"
    ]
)

service = build("gmail", "v1", credentials=creds)
today_utc = datetime.now(timezone.utc).date()

# Call the Gmail API
results = (
    service.users()
    .messages()
    .list(
        userId='me',
        labelIds=['INBOX'],
        q=f'category:primary after:{today_utc}'
    )
    .execute()
)

messages = results.get('messages', [])

if not messages:
    print("No new primary emails found today.")
else:
    print(f"Found {len(messages)} new email(s) in Primary today.")
    for msg in messages:
        msg_detail = (
            service.users()
            .messages()
            .get(
                userId='me', 
                id=msg['id']
            )
            .execute()
        )
        payload = msg_detail.get('payload', {})
        headers = payload.get('headers', [])

        # Extract email headers
        subject = next((header['value'] for header in headers if 
                        header['name'] == 'Subject'), 'No Subject')
        date = next((header['value'] for header in headers if 
                     header['name'] == 'Date'), 'No Date')
        sender = next((header['value'] for header in headers if 
                       header['name'] == 'From'), 'Unknown Sender')

        # Skip automated emails
        skip_keywords = ["noreply", "no-reply", "do-not-reply", "newsletter", "notifications", 
                         "mailer", "mailchimp", "hubspot", "job alert"]
        if any(keyword in sender.lower() for keyword in skip_keywords):
            print(f"⏭️ Skipping automated email from: {sender}")
            continue

        print(f"📩 Subject: {subject}")
        print(f"🕒 Date: {date}")
        print(f"👤 From: {sender}")

        # Extract plain text body
        email_body = ""
        if 'parts' in payload:
            for part in payload['parts']:
                if part['mimeType'] == 'text/plain':
                    data = part['body']['data']
                    decoded_bytes = base64.urlsafe_b64decode(
                        data.encode('UTF-8'))
                    body = decoded_bytes.decode('UTF-8')
                    break
        else:
            data = payload.get('body', {}).get('data')
            if data:
                decoded_bytes = base64.urlsafe_b64decode(data.encode('UTF-8'))
                body = decoded_bytes.decode('UTF-8')

        if body:
            print("📨 Email body preview:")
            print(body[:300], '...')
            print("🤖 Generating GPT-based response suggestion...")

            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a smart and helpful email assistant. "
                            "Your job is to read the email message provided and generate a short, professional, and relevant response. "
                            "If the email contains a question or request, respond clearly and directly. "
                            "If it's just an update or greeting, acknowledge it politely. "
                            "Avoid generic phrases. Personalize the tone if possible."
                        )
                    },
                    {          
                        "role": "user",
                        "content": email_body
                    }
                ],
                temperature=0.5,
                max_tokens=200
            )

            suggestion = response.choices[0].message.content
            print("💡 Suggested Response:")
            print(suggestion)
            print("=" * 50)
    