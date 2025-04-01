def is_likely_newsletter(headers, subject, body):
    """
    Applies rules to determine whether an email is a newsletter or bulk message.
    Returns True if the email is likely a newsletter; False otherwise.
    """
    subject = subject.lower()
    body = body.lower()

    # Check common newsletter keywords
    newsletter_keywords = ["newsletter", "daily digest", "roundup", "what you missed", "in case you missed it"]
    if any(keyword in subject for keyword in newsletter_keywords):
        return True

    # Check for typical headers
    list_unsubscribe = any(h["name"].lower() == "list-unsubscribe" for h in headers)
    if list_unsubscribe:
        return True

    # Check sender domains that often send bulk mail
    sender = next((h["value"] for h in headers if h["name"].lower() == "from"), "").lower()
    bulk_domains = ["medium.com", "ziprecruiter", "substack.com", "newsletters", "jobs@", "no-reply@", "glassdoor", "linkedin"]
    if any(domain in sender for domain in bulk_domains):
        return True

    # Check for unsubscribe links in body
    if "unsubscribe" in body:
        return True

    return False