from dotenv import load_dotenv
import os
from pathlib import Path
import imaplib
import email
import json
import traceback

def initiate_mail_client():
    env_path = (
            Path(__file__).parent.parent.parent
            / "config"
            / "mail_settings.env"
    )
    load_dotenv(env_path)

    email_address = os.getenv("EMAIL_ADDRESS")
    password = os.getenv("EMAIL_PASSWORD")

    mail = imaplib.IMAP4_SSL("imap.gmail.com")
    mail.login(email_address, password)
    return mail

def get_new_mails():
    mail = initiate_mail_client()
    mail.select("Surfreport")

    status, messages = mail.search(
        None,
        "ALL"
    )
    mail_ids = messages[0].split()

    dataFromMail = []
    for mail_id in mail_ids:
        status, msg_data = mail.fetch(mail_id,"(RFC822)")
        message = email.message_from_bytes(msg_data[0][1])
        if message["Subject"] == "surfreport":
            if message.is_multipart():
                for part in message.walk():
                    content_type = part.get_content_type()
                    if content_type == "text/plain":
                        body = part.get_payload(
                            decode=True
                        ).decode()

                        jsonData = json.loads(body)
                        jsonData['mailId'] = mail_id
                        dataFromMail.append(jsonData)
    return dataFromMail

def move_mail(mailId):
    try:
        mailId = b'1'
        mail = initiate_mail_client()
        mail.select("Surfreport")
        mail.copy(mailId, "Used surfreport")

        mail.store(mailId, '+FLAGS', '\\Deleted')

        mail.expunge()
    except Exception:
        traceback.print_exc()