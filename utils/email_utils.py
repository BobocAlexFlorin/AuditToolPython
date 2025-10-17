import smtplib
from email.mime.text import MIMEText

# Hardcoded mapping of usernames to emails
USER_EMAILS = {
    "uig99939": "alexandru-florin.boboc@conti.de",
    "uih10432": "alexandru-florin.boboc@conti.de",
    "user3": "alexandru-florin.boboc@conti.de"
}

def send_responsible_email(responsible_username, audit_title):
    to_email = USER_EMAILS.get(responsible_username)
    if not to_email:
        return False  # No email found for user

    msg = MIMEText(f"You have been assigned as responsible for the audit: {audit_title}")
    msg["Subject"] = "New Audit Assignment"
    msg["From"] = "audit-tool@example.com"
    msg["To"] = to_email

    try:
        # For local testing, use a dummy SMTP server or your real SMTP server
        with smtplib.SMTP("localhost") as server:
            server.send_message(msg)
        return True
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False