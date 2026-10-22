"""Notification service — persist + email notifications."""

from typing import Optional
from uuid import UUID

from jinja2 import Template

from app.config.logging_config import get_logger
from app.config.settings import settings
from app.database.crud import notification_crud
from app.database.session import SessionLocal

logger = get_logger(__name__)


def create_notification(
    user_id: UUID,
    type: str,
    title: str,
    body: Optional[str] = None,
    link: Optional[str] = None,
) -> None:
    """Persist a notification to the database for a user."""
    db = SessionLocal()
    try:
        notification_crud.create(
            db,
            user_id=user_id,
            type=type,
            title=title,
            body=body,
            link=link,
        )
    except Exception as exc:
        logger.warning(f"Failed to create notification: {exc}")
    finally:
        db.close()


class NotificationService:
    """Email delivery (SMTP)."""

    @staticmethod
    def _render(template_str: str, context: dict) -> str:
        return Template(template_str).render(**context)

    @staticmethod
    async def send_email(to_email, subject, html_body, text_body=None):
        if not settings.SMTP_HOST or not settings.SMTP_USER:
            logger.info("SMTP not configured — skipping email.")
            return False
        try:
            import aiosmtplib
            from email.mime.multipart import MIMEMultipart
            from email.mime.text import MIMEText

            message = MIMEMultipart("alternative")
            message["From"] = settings.SMTP_FROM_EMAIL
            message["To"] = to_email
            message["Subject"] = subject
            if text_body:
                message.attach(MIMEText(text_body, "plain"))
            message.attach(MIMEText(html_body, "html"))

            await aiosmtplib.send(
                message,
                hostname=settings.SMTP_HOST,
                port=settings.SMTP_PORT,
                username=settings.SMTP_USER,
                password=settings.SMTP_PASSWORD,
                start_tls=settings.SMTP_USE_TLS,
                timeout=30,
            )
            return True
        except Exception as exc:
            logger.error(f"Email send failed: {exc}")
            return False

    @staticmethod
    async def send_research_complete(to_email, company_name, report_title, report_url):
        html = NotificationService._render(
            """
            <html><body style="font-family:Arial,sans-serif;">
              <h2>Research Complete: {{ company }}</h2>
              <p>Your market research report for <strong>{{ company }}</strong> is ready.</p>
              <p><strong>{{ title }}</strong></p>
              <p><a href="{{ url }}">View Report</a></p>
            </body></html>
            """,
            {"company": company_name, "title": report_title, "url": report_url},
        )
        return await NotificationService.send_email(
            to_email, f"Research Ready: {company_name}", html
        )