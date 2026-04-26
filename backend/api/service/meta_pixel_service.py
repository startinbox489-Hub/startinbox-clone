"""
META PIXEL
"""

import time
import hashlib
from typing import Any, Dict

import httpx

from api.core.config import settings
from api.utils.task_logger import create_logger

logger = create_logger()


# TODO: Add to payment webhooks if implemented
class MetaPixelService:
    """
    MetaPixelService
    """

    @staticmethod
    def sha256_hash(value: str) -> str:
        """
        Hash value
        """
        return hashlib.sha256(value.strip().lower().encode()).hexdigest()

    @staticmethod
    async def send_meta_event(
        event_name: str,
        event_id: str,
        email: str,
        custom_data: Dict[str, Any],
    ) -> None:
        """
        Sends meta event with deduplication.
        
        curl -X POST \
            -F 'data=[
                {
                    "event_name": "Purchase",
                    "event_time": 1762902353,
                    "user_data": {
                    "em": [
                        "309a0a5c3e211326ae75ca18196d301a9bdbd1a882a4d2569511033da23f0abd"
                    ],
                    "ph": [
                        "254aa248acb47dd654ca3ea53f48c2c26d641d23d7e2e93a1ec56258df7674c4",
                        "6f4fcb9deaeadc8f9746ae76d97ce1239e98b404efe5da3ee0b7149740f89ad6"
                    ],
                    "client_ip_address": "123.123.123.123",
                    "client_user_agent": "$CLIENT_USER_AGENT",
                    "fbc": "fb.1.1554763741205.AbCdEfGhIjKlMnOpQrStUvWxYz1234567890",
                    "fbp": "fb.1.1558571054389.1098115397"
                    },
                    "custom_data": {
                    "currency": "usd",
                    "value": 123.45,
                    "contents": [
                        {
                        "id": "product123",
                        "quantity": 1,
                        "delivery_category": "home_delivery"
                        }
                    ]
                    },
                    "event_source_url": "http://jaspers-market.com/product/123",
                    "action_source": "website"
                }
                ]' \
            -F 'access_token=<ACCESS_TOKEN>' \
            https://graph.facebook.com/v24.0/<PIXEL_ID>/events
        """
        payload = {
            "data": [
                {
                    "event_name": event_name,
                    "event_time": int(time.time()),
                    "event_id": event_id,
                    "user_data": {
                        "em": [MetaPixelService.sha256_hash(value=email)],
                    },
                    "custom_data": custom_data,
                    "action_source": "website",
                },
            ],
        }
        try:

            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.post(
                    settings.meta_pixel_url,
                    params={"access_token": settings.meta_pixel_access_token},
                    json=payload,
                )
                if response.status_code in [201, 200]:
                    print(response.json())
                    return
                print(response.text)
        except Exception as exc:
            logger.warning(
                "Error sending events to meta pixel. event_name: %s, event_id: %s, email: %s, error: %s",
                event_name,
                event_id,
                email,
                str(exc),
            )
