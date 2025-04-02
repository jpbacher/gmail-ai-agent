def is_likely_automated_email(headers, subject, body):
    """
    Applies rules to determine whether an email is an automated or bulk message.
    Returns True if the email is likely a newsletter; False otherwise.
    """
    subject = subject.lower()
    body = body.lower()

    # Check common newsletter keywords
    auto_keywords = [
        "unsubscribe",
        "list-unsubscribe",
        "opt-out",
        "no-reply",
        "you are receiving this",
        "newsletter",
        "terms and conditions",
        "privacy policy",
        "do not reply",
        "update our terms",
        "no action required",
        "this is an automated message",
        "click here to view in browser",
        "notification",
        "alert"
    ]

    for keyword in auto_keywords:
        if keyword in subject or keyword in body:
            return True

    return False


def is_bulk_sender(sender: str) -> bool:
    """
    Determines whether an email is from a bulk sender based on known 
    domains or patterns.
    """
    sender = sender.lower()
    bulk_domains = [
        "medium.com", 
        "ziprecruiter", 
        "substack.com",
        "newsletters", 
        "jobs@", 
        "no-reply@", 
        "glassdoor", 
        "linkedin"
    ]
    return any(domain in sender for domain in bulk_domains)
