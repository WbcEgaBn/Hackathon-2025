import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os
from dotenv import load_dotenv

load_dotenv()

EMAIL_HOST = os.getenv("EMAIL_HOST", "smtp.gmail.com")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", 587))
EMAIL_USERNAME = os.getenv("EMAIL_USERNAME")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
FROM_EMAIL = EMAIL_USERNAME


def send_email(to, subject, html_body):
    if not EMAIL_USERNAME or not EMAIL_PASSWORD:
        print("EMAIL_USERNAME or EMAIL_PASSWORD not set in .env")
        return

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = FROM_EMAIL
    msg["To"] = to

    msg.attach(MIMEText(html_body, "html"))

    try:
        with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT) as server:
            server.starttls()
            server.login(EMAIL_USERNAME, EMAIL_PASSWORD)
            server.sendmail(FROM_EMAIL, [to], msg.as_string())
        print(f"Successfully sent to {to}")
    except Exception as e:
        print(f"Email send failed: {e}")
