"""
WhatsappService supporting Twilio + Meta Cloud API
"""

import os
from typing import List, Optional
import mimetypes

from twilio.rest import Client
from twilio.base.exceptions import TwilioException, TwilioRestException
from httpx import AsyncClient as async_client, RequestError, NetworkError, ConnectError

from api.utils.task_logger import create_logger
from api.utils.custom_exceptions import CustomMetaException
from api.core.config import settings

logger = create_logger(":: WHATSAPP SERVICE ::")


class WhatsappService:
    """
    Whtsapp service using Twilio WhatsApp API
    """

    def __init__(self, provider: str = "twilio") -> None:
        """
        Constructor
        """
        self.provider = provider.lower()
        self.path = os.path.join(os.getcwd(), "startup_reports")

        if self.provider == "twilio":
            try:
                self.from_number = f"whatsapp:{settings.twilio_whatsapp_number}"
                self.client = Client(
                    settings.twilio_account_sid,
                    settings.twilio_auth_token,
                )
                return
            except Exception as exc:
                logger.error("Error intiating twilio sdk: %s", str(exc))
                raise CustomMetaException() from exc
        if self.provider == "meta":
            self.graph_api_url = (
                f"{settings.meta_graph_url}/{settings.meta_phone_number_id}/messages"
            )
            self.meta_upload_url = (
                f"{settings.meta_graph_url}/{settings.meta_app_id}/media"
            )
            return

        raise CustomMetaException(
            "Whatsapp message provider must be one of meta or twilio"
        )

    # ================= TWILIO ================= #
    def _send_twilio(
        self,
        to_number: str,
        body: str,
        attachments: Optional[List[str]] = None,
    ) -> dict:
        """
        Sends message to whatsapp via twillio.

        Args:
            attachments (list[str]): List of url path to the file.
        """
        to_number = f"whatsapp:{to_number}"

        try:
            message = self.client.messages.create(
                from_=self.from_number,
                body=body,
                to=to_number,
                media_url=attachments if attachments else None,
            )
            logger.info("Twilio WhatsApp sent → SID %s", message.sid)
            logger.info("Twilio error message %s", message.error_message)
            return {"success": True, "sid": message.sid}
        except (TwilioException, TwilioRestException) as exc:
            logger.error("Twilio WhatsApp error: %s", str(exc))
            return {"success": False, "error": str(exc)}

    # ================= META ================= #
    async def _send_meta(
        self, to_number: str, body: str, attachments: Optional[List[str]] = None
    ) -> dict:
        """
        Uses Meta WhatsApp Cloud API
        attachments → list of local file paths (will be uploaded)
        """
        headers = {
            "Authorization": f"Bearer {settings.meta_whatsapp_token}",
        }

        # Step 1: Upload media if provided
        media_ids = []
        if attachments:

            for file_name in attachments:
                file_path = os.path.join(self.path, file_name)
                mime_type, _ = mimetypes.guess_type(file_path)
                if not mime_type or file_name.endswith("pdf"):
                    mime_type = "application/pdf"
                elif not mime_type or file_name.endswith("docx"):
                    mime_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                try:

                    with open(file_path, "rb") as f:
                        files = {"file": (os.path.basename(file_path), f, mime_type)}
                        file_data = {
                            "messaging_product": "whatsapp",
                            "type": "document",
                        }
                        async with async_client() as aclient:
                            resp = await aclient.post(
                                self.meta_upload_url,
                                headers=headers,
                                files=files,
                                data=file_data,
                                timeout=20.0,
                            )
                            # resp.raise_for_status()
                            data = resp.json()
                            if data.get("error"):
                                logger.warning("media upload error: %s", str(data))
                            media_ids.append(data.get("id"))
                except (RequestError, NetworkError, ConnectError) as exc:
                    logger.error("❌ Meta upload error for %s: %s", file_path, str(exc))
                    raise exc

        # Step 2: Send message
        payload = {
            "messaging_product": "whatsapp",
            "to": to_number,
            "type": "text",
            "text": {"body": body},
        }

        results = []
        try:
            # send text message first
            async with async_client() as aclient:
                resp = await aclient.post(
                    self.graph_api_url,
                    headers=headers,
                    json=payload,
                    timeout=20.0,
                )
                message_data = resp.json()
                if message_data.get("error"):
                    logger.warning("Send message error: %s", str(message_data))
                results.append(message_data)

            # send each media
            for media_id in media_ids:
                payload_media = {
                    "messaging_product": "whatsapp",
                    "to": to_number,
                    "type": "document",
                    "document": {"id": media_id},
                }
                async with async_client() as aclient:
                    resp_media = await aclient.post(
                        self.graph_api_url,
                        headers=headers,
                        json=payload_media,
                        timeout=20.0,
                    )
                    message_media_data = resp.json()
                    if message_media_data.get("error"):
                        logger.warning(
                            "Send message media error: %s", str(message_media_data)
                        )
                    results.append(resp_media.json())

            logger.info("✅ Meta WhatsApp sent successfully")
            return {"success": True, "results": results}

        except (RequestError, NetworkError, ConnectError) as exc:
            logger.error("❌ Meta WhatsApp send error: %s", str(exc))
            return {"success": False, "error": str(exc)}
        except Exception as exc:
            logger.error("❌ Meta WhatsApp send error: %s", str(exc))
            return {"success": False, "error": str(exc)}

    # ================= PUBLIC ================= #
    async def send_message(
        self, to_number: str, body: str, attachments: Optional[List[str]] = None
    ) -> dict:
        """
        Sends whatsapp message depending on the intended provider.

        Usage:

            .. code-block:: python


        twilio_ws = WhatsappService(provider="twilio")
        await twilio_ws.send_message(
            to_number="+2348012345678",
            body="🚀 Your startup report is ready!",
            attachments=["https://domain.com/reports/idea123.pdf"]  # Twilio (needs public URLs)
        )


        meta_ws = WhatsappService(provider="meta")
        await meta_ws.send_message(
            to_number="2348012345678",  # no "whatsapp:" prefix needed
            body="🚀 Your startup report is ready!",
            attachments=["pdfs/idea123.pdf", "docs/idea123.docx"]  # Meta (can send local files directly)
        )
        """
        try:
            if self.provider == "twilio":
                return self._send_twilio(to_number, body, attachments)
            if self.provider == "meta":
                return await self._send_meta(to_number, body, attachments)
            raise ValueError("Provider must be either 'twilio' or 'meta'")
        except Exception as exc:
            logger.error("Error: %s", str(exc))
            raise CustomMetaException() from exc
