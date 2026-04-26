"""
Send Grid Email SERVICE
"""

import os
from typing import List, Optional, Any, Dict
import base64
from pathlib import Path

from httpx import AsyncClient, HTTPStatusError
from jinja2 import Template, Environment, FileSystemLoader, TemplateNotFound
from api.utils.task_logger import create_logger
from api.core.config import settings

logger = create_logger(":: SendGridMailService ::")

template_env = Environment(loader=FileSystemLoader("templates"))


class SendGridMailService:
    """
    SendGridMail Service for sending emails with templates and attachments
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        self.send_grid_api_key = settings.send_grid_api_key
        self.send_grid_from_email = settings.send_grid_from_mail
        self.send_grid_base_url = settings.send_grid_mail_base_url

    def __render_template(self, template_name: str, context: Dict[str, Any]) -> str:
        """
        Render Jinja2 template with context data.

        Args:
            template_name (str): The name of the template.
            context (Dict[str, Any]): The data to be embedded inside the email template.
        Returns:
            template (str): The rendered template as string.
        Raises:
            TemplateNotFound: if Template missing.
            Exception: For any general exception.
        """
        try:
            template = template_env.get_template(template_name)
            return template.render(**context)
        except TemplateNotFound as exc:
            logger.error("Template not found: %s", template_name)
            raise exc
        except Exception as exc:
            logger.error("Template rendering error for %s: %s", template_name, str(exc))
            raise exc

    def __encode_attachment(
        self,
        file_content: bytes,
        filename: str,
        content_type: str = "application/octet-stream",
    ) -> Dict[str, str]:
        """
        Encode file attachment for SendGrid.
        """
        return {
            "content": base64.b64encode(file_content).decode("utf-8"),
            "filename": filename,
            "type": content_type,
            "disposition": "attachment",
        }

    async def __read_and_encode_attachments(
        self, attachment_file_names: List[str]
    ) -> List[Dict[str, str]]:
        """
        Read files from disk and encode them as attachments.
        """
        attachments = []
        for file_name in attachment_file_names:
            file_path = (
                os.path.join(os.getcwd(), "startup_reports", "pdfs", file_name)
                if file_name.endswith(".pdf")
                else os.path.join(os.getcwd(), "startup_reports", "docs", file_name)
            )
            try:
                path = Path(file_path)
                if not path.exists():
                    logger.warning("Attachment file not found: %s", file_path)
                    continue

                with open(path, "rb") as file:
                    file_content = file.read()

                # Determine content type based on file extension
                content_type = self._get_content_type(path.suffix.lower())

                attachment = self.__encode_attachment(
                    file_content, path.name, content_type
                )
                attachments.append(attachment)
                logger.info("Successfully encoded attachment: %s", path.name)

            except Exception as exc:
                logger.error("Failed to read attachment %s: %s", file_path, str(exc))
                continue

        return attachments

    def _get_content_type(self, file_extension: str) -> str:
        """Map file extensions to MIME types"""
        content_types = {
            ".pdf": "application/pdf",
            ".doc": "application/msword",
            ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            ".txt": "text/plain",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".png": "image/png",
            ".gif": "image/gif",
            ".zip": "application/zip",
            ".xls": "application/vnd.ms-excel",
            ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        }
        return content_types.get(file_extension, "application/octet-stream")

    async def send_email_via_sendgrid(
        self,
        to: str,
        subject: str,
        html_content: Optional[str] = None,
        text_content: Optional[str] = None,
        attachments: Optional[List[Dict[str, str]]] = None,
    ) -> bool:
        """
        Send email using SendGrid API with support for HTML and attachments.

        Args:
            to (str): Recipient email address
            subject (str): Email subject
            html_content (str, optional): HTML content of the email
            text_content (str, optional): Plain text content of the email
            attachments (List[Dict], optional): List of encoded attachments

        Returns:
            bool: True if email was sent successfully, False otherwise
        """
        headers = {
            "Authorization": f"Bearer {self.send_grid_api_key}",
            "Content-Type": "application/json",
        }

        # Build content array
        content = []
        if html_content:
            content.append({"type": "text/html", "value": html_content})
        if text_content:
            content.append({"type": "text/plain", "value": text_content})

        # If no content provided, use empty text
        if not content:
            content.append({"type": "text/plain", "value": ""})

        data = {
            "personalizations": [{"to": [{"email": to}]}],
            "from": {
                "email": self.send_grid_from_email,
                "name": settings.app_name,
            },
            "subject": subject,
            "content": content,
        }

        # Add attachments if provided
        if attachments:
            data["attachments"] = attachments

        try:
            async with AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    self.send_grid_base_url, json=data, headers=headers
                )
                response.raise_for_status()
                logger.info("Email successfully sent to %s", to)
                return True

        except HTTPStatusError as exc:
            logger.error(
                "SendGrid API error: %s - %s",
                exc.response.status_code,
                exc.response.text,
            )
            return False
        except Exception as exc:
            logger.error("Failed to send email to %s: %s", to, str(exc))
            return False

    async def send_templated_email(
        self,
        to: str,
        subject: str,
        template_name: Optional[str] = None,
        template_data: Optional[Dict[str, Any]] = None,
        plain_message: Optional[str] = None,
        attachment_file_names: Optional[List[str]] = None,
    ) -> bool:
        """
        Send email with template support.

        Args:
            to (str): Recipient email address
            subject (str): Email subject
            template_name (str, optional): Name of the template file
            template_data (Dict, optional): Data to render in the template
            plain_message (str, optional): Plain text fallback message
            attachment_file_names (List[str], optional): List of file paths to attach

        Returns:
            bool: True if email was sent successfully, False otherwise

        Usage:
            .. code-block:: python

                success = await send_grid_mail_service.send_templated_email(
                    to="user@example.com",
                    subject="Welcome!",
                    template_name="welcome_email.html",
                    template_data={"username": "John", "features": ["Feature1", "Feature2"]},
                    attachment_paths=["welcome.pdf"]
                )
        """
        html_content = None
        text_content = plain_message
        attachments = None

        # Render template if provided
        if template_name:
            try:
                html_content = self.__render_template(
                    template_name, template_data or {}
                )
                # If no plain message provided, create a simple text version
                if not text_content:
                    text_content = (
                        "Please view this email in an HTML-compatible client."
                    )
            except Exception as exc:
                logger.error(
                    "Failed to render template %s: %s", template_name, str(exc)
                )
                raise exc

        # Process attachments if provided
        if attachment_file_names:
            attachments = await self.__read_and_encode_attachments(
                attachment_file_names
            )

        return await self.send_email_via_sendgrid(
            to=to,
            subject=subject,
            html_content=html_content,
            text_content=text_content,
            attachments=attachments,
        )

    async def send_bulk_templated_emails(
        self,
        recipients: List[Dict[str, Any]],
        subject: str,
        template_name: str,
        common_template_data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, List[str]]:
        """
        Send templated emails to multiple recipients.

        Args:
            recipients: List of dicts with 'email' and optional 'template_data'
            subject: Email subject
            template_name: Template to use
            common_template_data: Data applied to all emails

        Returns:
            Dict with 'success' and 'failed' lists
        """
        results = {"success": [], "failed": []}
        common_data = common_template_data or {}

        for recipient in recipients:
            email = recipient["email"]
            recipient_data = recipient.get("template_data", {})

            # Merge common data with recipient-specific data
            template_data = {**common_data, **recipient_data}

            success = await self.send_templated_email(
                to=email,
                subject=subject,
                template_name=template_name,
                template_data=template_data,
            )

            if success:
                results["success"].append(email)
            else:
                results["failed"].append(email)

        logger.info(
            "Bulk email send completed: %s successful, %s failed",
            len(results["success"]),
            len(results["failed"]),
        )
        return results


send_grid_mail_service = SendGridMailService()
