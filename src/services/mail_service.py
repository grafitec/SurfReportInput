from dotenv import load_dotenv
import os
from pathlib import Path
import imaplib

def initiate_mail_client():
    env_path = (
            Path(__file__).parent.parent.parent
            / "config"
            / "mail_settings.env"
    )
    load_dotenv(env_path)

    email = os.getenv("EMAIL_ADDRESS")
    password = os.getenv("EMAIL_PASSWORD")

    mail = imaplib.IMAP4_SSL("imap.gmail.com")
    mail.login(email, password)

    mail.select("INBOX")
    status, messages = mail.search(
        None,
        "ALL"
    )

    print(messages)

