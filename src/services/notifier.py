from plyer import notification
import smtplib
from email.mime.text import MIMEText


def show_notification(title, message):
    notification.notify(
        title=title,
        message=message,
        timeout=10
    )


def send_email(to_email, subject, body):
    sender_email = "quocthangbon@gmail.com"
    app_password = "kzdsqmnbrsczilrm"

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = sender_email
    msg["To"] = to_email

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender_email, app_password)
            server.send_message(msg)
    except Exception as e:
        print("❌ Email error:", e)