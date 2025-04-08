import os
import boto3
import json
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

s3 = boto3.client(
    "s3",
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name=os.getenv("AWS_REGION"),
)

BUCKET_NAME = os.getenv("S3_BUCKET_NAME")


def save_response_to_s3(subject, sender, response):
    timestamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    safe_subject = subject.replace(" ", "_").replace("/", "_")[:100]
    key = f"responses/{timestamp}_{safe_subject}.json"

    data = {
        "subject": subject,
        "sender": sender,
        "response": response,
        "timestamp": timestamp
    }

    s3.put_object(Bucket=BUCKET_NAME, Key=key, Body=json.dumps(data))
    