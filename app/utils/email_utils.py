import logging
import smtplib
from email.message import EmailMessage

from app.core.config import settings

logger = logging.getLogger(__name__)

def send_email(to_email:str, subject:str, body:str):
    if not settings.MAIL_USERNAME or not settings.MAIL_PASSWORD:
        logger.info("SMTP not configured")
        return

    msg = EmailMessage()
    msg["SUBJECT"] = subject
    msg["FROM"] = settings.MAIL_FROM
    msg["TO"] = to_email
    msg.set_content(body)

    try:
        #plain, unencrypted TCP connection to the mail server
        with smtplib.SMTP(settings.MAIL_SERVER, settings.MAIL_PORT) as server:
            server.starttls()
            server.login(settings.MAIL_USERNAME, settings.MAIL_PASSWORD)
            server.send_message(msg)
        logger.info("Email sent", extra={"to": to_email, "subject": subject})
    except Exception:
        logger.exception(
            "Failed to send email",
            extra={"to": to_email, "subject": subject}
        )
        raise

def welcome_email(to_email:str, name:str):
    subject = "Welcome to SmartBlog!!"
    body = (
        f"Hi {name},\n\n"
        "Welcome to Smart Blog! Your account has been created successfully.\n"
        "Start writing your first post and share it with the world.\n\n"
        "- The Smart Blog Team"
    )
    send_email(to_email, subject, body)

def password_reset_link(to_email:str,reset_token:str):
    reset_link = f"{settings.FRONTEND_URL}/reset-password?token={reset_token}"
    subject = "Reset your Smart Blog password"
    body = (
        "We received a request to reset your password.\n\n"
        f"Click the link below to reset it (expires in "
        f"{settings.RESET_TOKEN_EXPIRE_MIN} minutes):\n\n"
        f"{reset_link}\n\n"
        "If you didn't request this, you can safely ignore this email."
    )
    send_email(to_email, subject, body)

def first_post_congrats_email(to_email:str, name:str, post_title:str):
    subject = "🎉 You published your first post!"
    body = (
        f"Hi {name},\n\n"
        f"Congratulations on publishing your first post: \"{post_title}\"!\n"
        "Keep writing, keep sharing.\n\n"
        "- The Smart Blog Team"
    )
    send_email(to_email, subject, body)