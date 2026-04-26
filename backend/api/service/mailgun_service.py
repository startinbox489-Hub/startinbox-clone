"""
MAILGUN SERVICE
"""

import os
from typing import List, Optional, Tuple
from io import BufferedReader

from httpx import AsyncClient

from api.core.config import settings


class MailgunService:
    """
    Mailgun Service
    """

    def __init__(self):
        """
        Constuctor
        """
        self.__api_key = settings.google_gemini_api_key
        self.__base_url = f"{settings.mailgun_base_url}/{settings.domain_name}"

    async def send_email(
        self,
        to: List[str],
        subject: str,
        from_email: str = settings.domain_email,
        text: Optional[str] = None,
        html: Optional[str] = None,
        attachments: Optional[List[str]] = None,  # file paths
    ) -> dict:
        """
        Sends emails via mailgun.

        Args:
            to (List[str]): List of emails to recieve the intended email.
            subject (str): The subject of the email.
            from_email (str): The email sender.
            text (str | None): The text to be sent as email.
            html (str | None): The html formated email to be sent.
            attachments (List[str] | None): The atatchments to be sent with email.
        Returns:
            dict: The response signifying successful or failure.

        Usage:

            .. code-block:: python

            import MailginService

            mg_service = MailgunService()

            result = mg_service.send_email(
                from_email="My App <noreply@mydomain.com>",
                to=["user@example.com"],
                subject="Your Startup Report",
                text="Here is your report attached.",
                attachments=["idea_report.pdf", "idea_report.docx"]
            )

            print(result
        """
        if not text and not html:
            raise RuntimeError("html or text missing for mailgun emailing")
        url = f"{self.__base_url}/messages"
        auth = ("api", self.__api_key)
        files: list[Tuple[str, BufferedReader]] = []
        data = {
            "from": from_email,
            "to": to,
            "subject": subject,
        }
        if text:
            data["text"] = text
        if html:
            data["html"] = html
        if attachments:
            for filename in attachments:
                directory = "docs" if filename.endswith(".docx") else "pdfs"
                file_path = f"{os.getcwd()}/startup_reports/{directory}/{filename}"
                files.append(
                    (
                        "attachment",
                        open(
                            file_path,
                            "rb",
                        ),
                    )
                )

        async with AsyncClient() as client:
            response = await client.post(
                url, auth=auth, data=data, files=(files or None), timeout=20.0
            )
        for _, f in files:
            f.close()

        if response.status_code == 200:
            return {
                "success": True,
                "message": "Email sent successfully",
                "id": response.json().get("id"),
                "status_code": response.status_code,
            }
        return {
            "success": False,
            "message": response.text,
            "status_code": response.status_code,
            "id": None,
        }


mailgun_service = MailgunService()
