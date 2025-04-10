import boto3
import json
import os
from datetime import datetime
from dotenv import load_dotenv
from utils.logger import get_logger


load_dotenv()

logger = get_logger(__name__)

BUCKET_NAME = os.getenv("S3_BUCKET_NAME")


def get_s3_client():
    return boto3.client(
        "s3",
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        region_name=os.getenv("AWS_REGION")
    )


def save_response_to_s3(response_type, subject, sender, response_body):
    """
    Saves an email response (approved, edited, or skipped) to an S3 bucket
    in a structured JSON format.

    Args:
        response_type (str): The type of response (e.g., "approved",
        "edited", or "skipped").
        subject (str): The subject of the original email.
        sender (str): The sender's email address.
        response_body (str): The body of the GPT-generated or edited response.

    Returns:
        dict: A dictionary containing:
            - "status": "success" or "error"
            - "s3_key" (str, optional): The S3 object key where the file was 
            stored (if successful)
            - "aws_response" (dict, optional): The full AWS S3 API response
            (if successful)
            - "error" (str, optional): The error message (if failed)
    """
    
    s3 = get_s3_client()
    now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"{subject.replace(' ', '_')}_{now}.json"
    key = f"{response_type}/{filename}"

    data = {
        "timestamp": now,
        "response_type": response_type,
        "subject": subject,
        "sender": sender,
        "response_body": response_body
    }

    json_data = json.dumps(data, indent=2)

    try:
        response = s3.put_object(
            Bucket=BUCKET_NAME,
            Key=key,
            Body=json_data,
            ContentType="application/json"
        )
        return {"status": "success", "s3_key": key, "aws_response": response}
    except Exception as e:
        logger.exception(f"❌ Failed to upload to S3: {e}")
        return {"status": "error", "error": str(e)}


def save_summary_to_s3(subject, sender, summary_text):
    """
    Saves an email summary to the S3 bucket under the 'summaries' folder.

    Args:
        subject (str): The subject of the email.
        sender (str): The sender's email address.
        summary_text (str): The GPT-generated summary content.

    Returns:
        dict: A dictionary containing:
            - "status": "success" or "error"
            - "s3_key" (str, optional): The S3 object key where the file was stored (if successful)
            - "aws_response" (dict, optional): The full AWS S3 API response (if successful)
            - "error" (str, optional): The error message (if failed)
    """
    now = datetime.utcnow().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"{subject.replace(' ', '_')}_{now}.json"
    key = f"summaries/{filename}"

    data = {
        "timestamp": now,
        "type": "summary",
        "subject": subject,
        "sender": sender,
        "summary": summary_text
    }

    json_data = json.dumps(data, indent=2)

    try:
        response = s3.put_object(
            Bucket=BUCKET_NAME,
            Key=key,
            Body=json_data,
            ContentType="application/json"
        )
        return {"status": "success", "s3_key": key, "aws_response": response}
    except Exception as e:
        logger.exception(f"❌ Failed to upload summary to S3: {e}")
        return {"status": "error", "error": str(e)}


def upload_log_file_to_s3(local_log_path, s3_log_folder):
    """
    Uploads the local app log file to the S3 bucket under a logs folder.
    The log file will be saved with a timestamp in the filename.

    Args:
        local_log_path (str): The path to the local log file.
        s3_log_folder (str): The S3 folder where the log file 
        will be uploaded.
    """
    
    s3 = get_s3_client()
    
    if not os.path.exists(local_log_path):
        logger.warning(f"No log file found at {local_log_path}")
        return

    timestamp = datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d_%H-%M-%S")
    s3_key = f"{s3_log_folder}/app_{timestamp}.log"

    try:
        with open(local_log_path, "rb") as f:
            s3.upload_fileobj(f, BUCKET_NAME, s3_key)
        logger.info(f"📤 Uploaded log file to S3: {s3_key}")
    except Exception as e:
        logger.exception(f"❌ Failed to upload log file: {e}")
