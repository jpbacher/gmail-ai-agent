import boto3
import json
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

BUCKET_NAME = os.getenv("S3_BUCKET_NAME")

s3 = boto3.client("s3")


def save_response_to_s3(response_type, subject, sender, response_body):
    """
    Saves a response (approved/edited/skipped) as a JSON object to S3.

    Args:
        response_type (str): 'approved', 'edited', or 'skipped'
        subject (str): Email subject line
        sender (str): Email sender
        response_body (str): The actual response content

    Returns:
        dict: The S3 put_object response
    """
    timestamp = datetime.now(
        datetime.timezone.utc
    ).strftime("%Y-%m-%dT%H-%M-%S")
    sanitized_subject = subject[:50].replace(' ', '_').replace('/', '-')
    filename = f"{sanitized_subject}_{timestamp}.json"
    key = f"{response_type}/{filename}"

    json_data = json.dumps({
        "subject": subject,
        "sender": sender,
        "response": response_body,
        "timestamp": timestamp
    })

    response = s3.put_object(
        Bucket=BUCKET_NAME,
        Key=key,
        Body=json_data,
        ContentType="application/json"
    )

    return response
