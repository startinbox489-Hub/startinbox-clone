"""
MailChimp Service
"""

import hashlib
import httpx

from api.core.config import settings
from api.utils.task_logger import create_logger

logger = create_logger(":: MalichimpService ::")


class MalichimpService:
    """
    MalichimpService
    """

    async def add_subscribers(self, email: str) -> dict:
        """
        Adds subscribers to mail chimp.
        status must be one of: subscribed | unsubscribed | cleaned | pending | transactional
        """
        url = f"{settings.mailchimp_base_url}/{settings.mailchimp_audience_id}/members"
        payload = {
            "email_address": email,
            "status": "subscribed",
        }
        try:
            async with httpx.AsyncClient(timeout=20.0) as client:
                response = await client.post(
                    url=url, json=payload, auth=("anything", settings.mailchimp_api_key)
                )
                data: dict = response.json()

                if (
                    response.status_code in [200, 201]
                    and data.get("status") == "subscribed"
                ):
                    data.update({"success": True})
                else:
                    logger.warning("Could not add email to mailchimp: %s", str(data))
                    data.update({"success": False})

                logger.info(
                    "Mail Subscribe Chimp Response: id: %s, status: %s",
                    data.get("id"),
                    data.get("status"),
                )

                return data
        except Exception as exc:
            logger.error("Error subscribibg email to mailchimp: %s", str(exc))
            return {"message": "Failed to subscribe email", "success": False}

    async def remove_subscribers(self, email: str) -> dict:
        """
        Remove subscribers from mail chimp
        """
        member_id = hashlib.md5(email.encode()).hexdigest()
        url = f"{settings.mailchimp_base_url}/{settings.mailchimp_audience_id}/members/{member_id}"
        payload = {
            "status": "unsubscribed",
        }
        try:
            async with httpx.AsyncClient(timeout=20.0) as client:
                response = await client.put(
                    url=url, json=payload, auth=("anything", settings.mailchimp_api_key)
                )
                data: dict = response.json()

                if response.status_code in [200, 201]:
                    data.update({"success": True})
                else:
                    logger.warning(
                        "Could not remove email from mailchimp: %s", str(data)
                    )
                    data.update({"success": False})

                logger.info(
                    "Mail Unsubscribe Chimp Response: id: %s, status: %s",
                    data.get("id"),
                    data.get("status"),
                )

                return data
        except Exception as exc:
            logger.error("Error un-subscribibg email to mailchimp: %s", str(exc))
            return {"message": "Failed to unsubscribe email", "success": False}


mailchimp_service = MalichimpService()
