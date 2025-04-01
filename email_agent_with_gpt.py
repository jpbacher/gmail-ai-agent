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

# just retrieve emails from today
today_utc = datetime.now(timezone.utc).date()

# Call the Gmail API and fetch emails from the Primary category
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

def is_likely_newsletter(headers, subject, body):
    
    subject_keywords = ['newsletter', 'digest', 'alert', 'update', 'job alert']
    content_keywords = ['unsubscribe', 'view in browser', 'manage preferences', 'click here']
    from_mailing_list = any(h['name'].lower() == 'list-unsubscribe' for h in headers)
    subject_match = any(keyword in subject.lower() for keyword in subject_keywords)
    body_match = any(keyword in body.lower() for keyword in content_keywords)

    return from_mailing_list or subject_match or body_match


summary = {"processed": 0, "skipped": 0, "skipped_subjects": []}

if not messages:
    print("No new primary emails found today.")
else:
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
        subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
        sender = next((h['value'] for h in headers if h['name'] == 'From'), 'No Sender')

        # Extract email body
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

        if is_likely_newsletter(headers, subject, body):
            print(f"⛔ Skipping likely newsletter or mass email from: {sender} | Subject: {subject}")
            summary["skipped"] += 1
            summary["skipped_subjects"].append(subject)
            continue

        print(f"📩 Subject: {subject}")
        print(f"🧠 From: {sender}")
        print("📨 Email body preview:")
        print(body[:300], '...')

        print("🤖 Generating GPT-based response suggestion...")

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a helpful assistant that writes short, professional email replies to real people. "
                        "Avoid responding to newsletters, promotions, or auto-generated emails."
                    )
                },
                {
                    "role": "user",
                    "content": body
                }
            ],
            temperature=0.7,
            max_tokens=150
        )    

        suggestion = response.choices[0].message.content
        print("💡 Suggested Response:")
        print(suggestion)
        print("=" * 75)
        summary["processed"] += 1
    
    print("=" * 75)
    print("📊 Summary:")
    print(f"✅ Processed human-like emails: {summary['processed']}")
    print(f"🚫 Emails skipped: {summary['skipped']}")
    if summary["skipped_subjects"]:
        print("🚫 Skipped subjects:")
        for subject in summary["skipped_subjects"]:
            print(f" - {subject}")
    print("=" * 75)
