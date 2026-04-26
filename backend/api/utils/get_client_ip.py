"""
Get Client IP
"""

from fastapi import Request

from api.schema.default_response_schema import CustomRequest
from api.utils.task_logger import create_logger

logger = create_logger(__name__)


def get_client_ip_render(request: CustomRequest | Request) -> str:
    """
    Get client ip
    """
    # Cloudflare header (Render uses CF infrastructure)
    cf_ip = request.headers.get("cf-connecting-ip")
    if cf_ip:
        logger.info("cf_ip: %s", cf_ip)
        return cf_ip

    x_forwarded_for = request.headers.get("x-forwarded-for")
    if x_forwarded_for:
        logger.info("x_forwarded_for: %s", x_forwarded_for)
        # the LAST IP because Render appends the real
        # connection IP to the end of any user-supplied chain.
        ips = [ip.strip() for ip in x_forwarded_for.split(",") if ip.strip() != ""]
        if len(ips) > 0:
            return ips[-1]

    return request.client.host if request.client else "127.0.0.1"
