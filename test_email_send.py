from notifications.email_sender import send_email

def main():
    html = """
    <html>
    <body>
        <h2>Test CivicDigest Email</h2>
        <p>If you see this, SMTP + Gmail App Password is working 🎉</p>
    </body>
    </html>
    """

    send_email(
        to="ryanenriquez65@gmail.com",
        subject="CivicDigest Test Email",
        html_body=html
    )

if __name__ == "__main__":
    main()
