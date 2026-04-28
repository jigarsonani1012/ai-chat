import smtplib
from email.message import EmailMessage
from smtplib import SMTPException

from app.core.config import settings


class EmailService:
    def send(self, to_email: str, subject: str, body: str) -> None:
        message = EmailMessage()
        message["From"] = settings.smtp_from
        message["To"] = to_email
        message["Subject"] = subject
        message.set_content(body)

        try:
            with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as smtp:
                if settings.smtp_username and settings.smtp_password:
                    smtp.login(settings.smtp_username, settings.smtp_password)
                smtp.send_message(message)
        except (OSError, SMTPException):
            if settings.app_env != "production":
                print(f"[dev-email] to={to_email} subject={subject}")
            else:
                raise
