"""
ResendEmailService - Using official 'resend' SDK with Jinja2 Templating
"""

import os
import base64
from typing import List, Optional, Dict, Any, TypedDict
from datetime import date

from jinja2 import Environment, FileSystemLoader, TemplateNotFound
import resend
from resend.exceptions import ResendError

from api.utils.task_logger import create_logger
from api.core.config import settings

logger = create_logger(":: ResendEmailService ::")


class SendResponse(TypedDict):
    """
    SendResponse is the type that wraps the response of the email that was sent.

    Attributes:
        id (str): The ID of the sent email
    """

    id: str
    """
    The sent Email ID.
    """


class ResendEmailService:
    """
    Resend email sender using the official Python SDK, Jinja2, and attachments.
    """

    DEFAULT_FROM_EMAIL = settings.resend_mail_default_email
    INFO_FROM_EMAIL = settings.resend_mail_info_email

    def __init__(self):
        """
        Constructor.
        Initializes the Resend client and Jinja2 environment.
        """
        resend.api_key = settings.resend_mail_api_key

        template_dir = os.path.join(os.getcwd(), "templates")
        self.jinja_env = Environment(loader=FileSystemLoader(template_dir))
        logger.info(
            "Jinja2 environment initialized with template directory: %s", template_dir
        )

    def _prepare_attachment(self, path: str) -> Dict[str, str]:
        """
        Prepares a single file attachment for the 'resend' SDK payload.
        The SDK requires filename and content (base64 string).
        """
        if not os.path.exists(path):
            raise FileNotFoundError(f"Attachment not found: {path}")

        with open(path, "rb") as f:
            encoded_content = base64.b64encode(f.read()).decode("utf-8")

        return {
            "filename": os.path.basename(path),
            "content": encoded_content,
        }

    def send_email(
        self,
        to_email: str,
        subject: str = "Your Startup report is ready!",
        template_name: str = "startup-report.html",
        context_data: Optional[Dict[str, Any]] = None,
        attachments: Optional[List[str]] = None,
    ) -> SendResponse:
        """
        Sends an email using a Jinja2 template and optional attachments via the Resend SDK.

        Args:
            to_email(str): The recipient's email address.
            subject(str): The subject line of the email.
            template_name(str): The name of the Jinja2 HTML template file (e.g., "startup-report.html").
            context_data(dict[str, Any]): Dictionary of data to pass to the Jinja template for rendering.
            attachments(List[str]): List of absolute or relative file paths for attachments.
        Returns:
            The JSON response from the Resend API.
        """

        context = context_data or {}
        context.update({"current_year": date.year})

        try:
            email_template = self.jinja_env.get_template(template_name)
            html_body = email_template.render(context)
        except TemplateNotFound as exc:
            logger.error("Template %s not found. Error: %s", template_name, str(exc))
            raise TemplateNotFound(
                f"Email template not found: {template_name}"
            ) from exc

        params = {
            "from": (
                self.DEFAULT_FROM_EMAIL
                if template_name == "startup-report.html"
                else self.INFO_FROM_EMAIL
            ),
            "to": [to_email],
            "subject": subject,
            "html": html_body,
        }

        if attachments:
            params["attachments"] = [
                self._prepare_attachment(path) for path in attachments
            ]
        # print("sending email...")
        try:
            email_response = resend.Emails.send(params)  # type: ignore
            email_id = email_response.get("id")
            if email_id:
                logger.info(
                    "Email sent to email: %s, res_id: %s",
                    to_email,
                    email_id,
                )
            return email_response
        except ResendError as exc:
            logger.error("Resend SDK error: %s", str(exc))
            # raise RuntimeError(f"Resend SDK failed to send email: {exc}") from exc


resend_email_service = ResendEmailService()
