import base64

def extract_headers(payload):
    """
    Extracts commonly used email headers from the Gmail message payload.

    Args:
        payload (dict): The 'payload' section from a Gmail API message.

    Returns:
        tuple: subject (str), date (str), sender (str), headers (list of dicts)
    """
    headers = payload.get('headers', [])
    header_dict = {h['name'].lower(): h['value'] for h in headers}
    subject = header_dict.get('subject', 'No Subject')
    date = header_dict.get('date', 'No Date')
    sender = header_dict.get('from', 'Unknown Sender')
    return subject, date, sender, headers


def extract_plain_text_body(payload):
    """
    Extracts and decodes the plain text content from the Gmail message payload.

    Args:
        payload (dict): The 'payload' section from a Gmail API message.

    Returns:
        str: Decoded plain text email body, or an empty string if not found.
    """
    if 'parts' in payload:
        for part in payload['parts']:
            if part['mimeType'] == 'text/plain':
                data = part['body'].get('data')
                if data:
                    return decode_base64(data)
    else:
        data = payload.get('body', {}).get('data')
        if data:
            return decode_base64(data)
    return ""


def decode_base64(data):
    """
    Decodes a base64-encoded string using URL-safe encoding.

    Args:
        data (str): Base64-encoded string.

    Returns:
        str: Decoded UTF-8 string.
    """
    decoded_bytes = base64.urlsafe_b64decode(data.encode("UTF-8"))
    return decoded_bytes.decode("UTF-8")