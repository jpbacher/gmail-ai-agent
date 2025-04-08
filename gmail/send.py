import base64
from email.mime.text import MIMEText
# from googleapiclient.discovery import build


def send_gmail_reply(
    service, message_id, thread_id, to_email, subject, reply_body
):
    """
    Sends a reply email using the Gmail API.

    Args:
        service: Authenticated Gmail API service instance.
        message_id: ID of the original message being replied to.
        thread_id: Thread ID to keep the reply in the conversation.
        to_email: Recipient's email address.
        subject: Email subject.
        reply_body: Body of the reply email.

    Returns:
        The sent message response from Gmail API.
    """

    message_text = f"Hi,\n\n{reply_body}\n\nBest,\nJosh Bacher"

    mime_message = MIMEText(message_text)
    mime_message["to"] = to_email
    mime_message["subject"] = f"Re: {subject}"
    mime_message["In-Reply-To"] = f"<{message_id}>"
    mime_message["References"] = f"<{message_id}>"

    raw_message = base64.urlsafe_b64encode(mime_message.as_bytes()).decode()

    return service.users().messages().send(
        userId="me",
        body={
            "raw": raw_message,
            "threadId": thread_id
        }
    ).execute()
