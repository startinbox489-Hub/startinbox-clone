"""
Keep Alive Loop
"""

import asyncio

import httpx

from api.utils.task_logger import create_logger
from api.core.config import settings

logger = create_logger(":: Keep Alive Util ::")


KEEPALIVE_INTERVAL_SECONDS = 3600  # 60 minutes
TARGET_URL = f"{settings.app_url}/api/v1/health"
TIMEOUT_SECONDS = 10


async def keepalive_loop(
    stop_event: asyncio.Event, interval: int = KEEPALIVE_INTERVAL_SECONDS
) -> None:
    """
    Periodically ping TARGET_URL until stop_event is set.
    """
    async with httpx.AsyncClient(timeout=TIMEOUT_SECONDS) as client:
        while not stop_event.is_set():
            try:
                # Add a small random jitter so repeated restarts don't synchronize pings
                await asyncio.sleep(
                    interval + (0.5 - asyncio.get_event_loop().time() % 1)
                )
                resp = await client.get(TARGET_URL)
                logger.info(
                    "Keepalive ping status=%s for %s", resp.status_code, TARGET_URL
                )
            except asyncio.CancelledError as exc:
                logger.info("Keepalive task cancelled. %s", str(exc))
                return
            except Exception as exc:
                logger.warning("Keepalive ping failed: %s", str(exc))
                # backoff a bit on failure

                try:
                    await asyncio.sleep(KEEPALIVE_INTERVAL_SECONDS)
                except asyncio.CancelledError:
                    logger.info("Keepalive task cancelled during backoff.")
                    return
