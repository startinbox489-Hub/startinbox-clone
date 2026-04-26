"""
User Location Service
"""

import sys
from typing import Dict
from httpx import AsyncClient, RequestError, NetworkError, ConnectError
import ipinfo

from api.utils.task_logger import create_logger
from api.core.config import settings

logger = create_logger(":: UserLocationService ::")

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")  # type: ignore


class UserLocationService:
    """
    User location service class
    """

    async def get_country_from_ip(self, ip: str) -> Dict[str, str]:
        """
        Lookup country info using ipapi.co API.
        Free ipapi.co has rate limits (30k/month, 1k/day)
        """
        if ip in ["127.0.0.1", "testclient"]:
            return {
                "country_code": "NG",
                "country_name": "Nigeria",
            }
        url = f"https://ipapi.co/{ip}/json/"

        try:
            async with AsyncClient(timeout=5.0) as aclient:
                response = await aclient.get(url)
                if response.status_code == 200:
                    data: dict = response.json()
                    print("data: ", data)
                    return {
                        "country_code": data.get("country", "USA"),
                        "country_name": data.get("country_name", "USA"),
                    }
        except (RequestError, NetworkError, ConnectError) as exc:
            logger.error("Error getting location from ip: %s", str(exc))
        return {
            "country_code": "USA",
            "country_name": "United States",
        }

    async def get_country_ipinfo(self, ip_address: str) -> Dict[str, str]:
        """
        Get country ipinfo
        """
        if ip_address in ["127.0.0.1", "testclient"]:
            return {
                "country_code": "NG",
                "country_name": "Nigeria",
            }

        try:
            # If no token is provided, it uses the public API (1k limit)
            # handler = ipinfo.getHandler(access_token=settings.ipinfo_api_key)
            handler = ipinfo.getHandlerAsync(access_token=None)
            details = await handler.getDetails(ip_address=ip_address, timeout=15)
            print("details: ", details.all)

            return {
                "country_code": details.country,  # 'US'
                "country_name": details.country_name,  # 'United States'
                # "is_eu": getattr(details, "is_eu", False),
            }
        except Exception as exc:
            logger.error("IPINFO. Error getting location from ip: %s", str(exc))

        return await self.get_country_from_ip(ip=ip_address)


user_location_service = UserLocationService()
