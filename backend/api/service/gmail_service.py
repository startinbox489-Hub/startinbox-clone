"""
Gmail service
"""

from datetime import date
from typing import Dict
from concurrent.futures import (
    ThreadPoolExecutor,
    TimeoutError as FutureTimeoutError,
)
import os
import smtplib
from email import encoders
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.nonmultipart import MIMENonMultipart  # for attachments
from jinja2 import Environment, FileSystemLoader, TemplateNotFound

from api.core.config import settings
from api.utils.task_logger import create_logger

logger = create_logger(":: GmailService ::")
# ThreadPoolExecutor instance
executor = ThreadPoolExecutor(max_workers=20)


class CustomGmailError(Exception):
    """
    CustomGmailError
    """

    def __init__(self, message: str = "Error sending email") -> None:
        """
        CustomGmailError constructor
        """
        super().__init__(message)


class GmailService:
    """
    Gmail service
    """

    async def __send_email(self, context: Dict[str, str | list]) -> None:
        """
        Sends email via gmail

        Args:
            context (dict): The dictionary of email contents

            e.g: context = {
            "recipient_email": schema.email,
            "email_subject": "Email Verification",
            "token": token_digits,
            "template_name": "welcome-verification.html",
            "first_name": "Dear",
            "attachments": ["docs/file.pdf", "pdfs/another_file.docx"]

        }
        """
        try:
            wdir = os.getcwd()
            template_dir = os.path.join(wdir, "templates")
            env = Environment(loader=FileSystemLoader(template_dir))

            template_name = context.get("template_name", "")
            assert isinstance(template_name, str)
            recipient_email = context.get("recipient_email", "")
            assert isinstance(recipient_email, str)
            email_subject = context.get("email_subject", "")
            assert isinstance(email_subject, str)
            attachments = context.get("attachments", [])
            try:
                email_template = env.get_template(template_name)
            except TemplateNotFound as exc:
                logger.error(
                    "Template %s not found in %s, \nerror: %s",
                    context.get("template_name"),
                    template_dir,
                    str(exc),
                )
                return

            html = email_template.render(
                {"attachments": attachments, "current_year": date.today().year}
            )

            # Create the email message
            message = MIMEMultipart("alternative")
            message["Subject"] = email_subject
            message["From"] = f'"StartInbox" <noreply@{settings.mail_username}>'
            message["To"] = recipient_email
            part = MIMEText(html, "html")
            message.attach(part)

            # attach files
            if attachments:
                for file_name in attachments:
                    try:
                        with open(
                            file=os.path.join(wdir, "startup_reports", file_name),
                            mode="rb",
                        ) as file:
                            file_part = MIMENonMultipart(
                                "application",
                                "octet-stream",
                            )
                            file_part.set_payload(file.read())
                            # set the content transfer encoding to base64,
                            # which is necessary for sending binary data over email.

                            encoders.encode_base64(file_part)
                            file_part.add_header(
                                "Content-Disposition",
                                "attachment",
                                filename=os.path.basename(file_name),
                            )
                            message.attach(file_part)
                    except FileNotFoundError as exc:
                        logger.warning("Email attachments not found: %s", str(exc))
                    except CustomGmailError as exc:
                        logger.error("Error attaching file %s: %s", file_name, str(exc))

            with smtplib.SMTP_SSL(settings.mail_server, settings.mail_port) as server:
                server.login(
                    settings.mail_username,
                    settings.mail_password,
                )
                server.sendmail(
                    settings.mail_username,
                    recipient_email,
                    message.as_string(),
                )
                logger.info("Email sent to: %s", recipient_email)
        except CustomGmailError as exc:
            logger.error("Error sending email: %s", str(exc))
            return

    async def send_email_route(self, context: dict):
        """
        Sends email using executor.

        Args:
            context (dict): The dictionary of email contents

            e.g: context = {
            "recipient_email": schema.email,
            "email_subject": "Your Startup Report is Ready",
            "template_name": "startup-report.html",
            "attachments": ["docs/file.pdf", "pdfs/another_file.docx"]

        }
        """
        try:
            future = executor.submit(self.__send_email, context)
            # Set a timeout for the task
            await future.result(timeout=10.0)  # Wait for the result
        except FutureTimeoutError:
            logger.error("Email sending timed out")
        except CustomGmailError as exc:
            logger.error("An error occurred: %s", exc)


gmail_service = GmailService()
