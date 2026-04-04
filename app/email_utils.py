import smtplib
from email.mime.text import MIMEText
import os

def send_reset_email(user_email, reset_url):

    sender_email = os.environ.get("EMAIL_USER")
    app_password = os.environ.get("EMAIL_PASS")



    subject = "Password Reset - Bag App"

    body = f"""
Hello,

Click the link below to reset your password:

{reset_url}
"""

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = f"Bag App <{sender_email}>"
    msg["To"] = user_email

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender_email, app_password)
            server.send_message(msg)
            print("✅ Email sent successfully")

    except Exception as e:
        print("❌ Email failed:", e)