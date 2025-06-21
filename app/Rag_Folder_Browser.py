# app/Rag_Folder_Browser.py

import smtplib
from email.mime.text import MIMEText
import os

def send_log_email():
    sender = os.environ["SMTP_SENDER"]
    password = os.environ["SMTP_PASSWORD"]
    receiver = os.environ["SMTP_RECEIVER"]

    subject = "📬 Weekly Activity Log"
    body = "This is your automated weekly activity summary from the Smart Document Assistant."

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = receiver

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender, password)
            server.sendmail(sender, [receiver], msg.as_string())
        print("✅ Email sent successfully.")
    except Exception as e:
        print(f"❌ Failed to send email: {e}")
