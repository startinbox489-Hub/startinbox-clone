"""
TwilioMetaService
"""

from typing import List

from twilio.rest import Client

from api.core.config import settings
from api.utils.task_logger import create_logger


logger = create_logger(":: TwilioMetaService ::")


class TwilioMetaService:
    """
    TwilioMetaService
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        self.__client = Client(
            settings.twilio_account_sid,
            settings.twilio_auth_token,
        )

    async def send_files(
        self, to_whatsapp_number: str, media_urls: None | List[str]
    ) -> None:
        """
        Send files to whatsapp
        """
        try:
            message = await self.__client.messages.create_async(
                to=to_whatsapp_number,
                from_=settings.twilio_whatsapp_number,
                body="Your Startup Reports are ready",
                media_url=media_urls,
            )
            logger.info("response body: %s", message.body)
        except Exception as exc:
            logger.error("Error sending report files: ", str(exc))
            raise exc


twilio_meta_service = TwilioMetaService()
