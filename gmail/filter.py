from typing import Tuple

# Keywords that are indicative of automated emails
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


def is_likely_automated_email(headers, subject, body) -> Tuple[bool, str]:
    """
    Applies rules to determine whether an email is an automated or bulk message.
    Returns True if the email is likely a newsletter; False otherwise.
    """
    sender = next((h["value"] for h in headers if h["name"].lower() == "from"), "").lower()

    if is_bulk_sender(sender):
        return True, f"Sender matches known bulk domains: {sender}"

    if any(h["name"].lower() == "list-unsubscribe" for h in headers):
        return True, "Header contains 'List-Unsubscribe'"

    for kw in auto_keywords:
        if kw in subject.lower():
            return True, f"Subject contains keyword: '{kw}'"

    for kw in auto_keywords:
        if kw in body.lower():
            return True, f"Body contains keyword: '{kw}'"

    return False, ""

