import os
import smtplib
from email.mime.text import MIMEText
from plyer import notification
from dotenv import load_dotenv

# Load biến môi trường
load_dotenv()


def show_notification(title, message):
    """Hiển thị popup notification"""
    try:
        notification.notify(
            title=title,
            message=message,
            app_name="EduFlow",
            timeout=10
        )

        print(f"🔔 Notification: {title} - {message}")

    except Exception as e:
        print(f"❌ Popup error: {e}")


def send_email(to_email, subject, body):

    sender_email = os.getenv("EMAIL_SENDER").strip()
    app_password = os.getenv("APP_PASSWORD").strip()

    if not sender_email or not app_password:
        print("❌ Thiếu EMAIL_SENDER hoặc APP_PASSWORD trong .env")
        return False

    msg = MIMEText(body, "plain", "utf-8")
    msg["Subject"] = subject
    msg["From"] = sender_email
    msg["To"] = to_email

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()

            server.login(sender_email, app_password)

            server.send_message(msg)

        print(f"✅ Đã gửi email tới {to_email}")
        return True

    except smtplib.SMTPAuthenticationError:
        print("❌ Sai Gmail hoặc App Password")
        return False

    except Exception as e:
        print(f"❌ Email error: {e}")
        return False