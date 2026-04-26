"""
URL SECRET SERVICE
"""

import hmac
import hashlib
import time
import base64
from urllib.parse import urlencode

from fastapi import HTTPException

from api.core.config import settings


class URLSecretService:
    """
    URLSecretService
    """

    @staticmethod
    def generate_signed_url(filename: str, expires_in: int = 180) -> str:
        """
        Generate a signed URL for a file with expiry (default 24h).

        Args:
            filename (str): The filename with .pdf or .docx extension
            expires_in (int): The period of expiration.

        Returns:
          file_url: str
        """
        expires_at = int(time.time()) + expires_in
        data = f"{filename}:{expires_at}".encode()
        secret = (settings.url_secret).encode()
        signature = hmac.new(secret, data, hashlib.sha256).digest()
        token = base64.urlsafe_b64encode(signature).decode().rstrip("=")
        query = urlencode({"expires": expires_at, "token": token})
        return f"{settings.app_url}/api/v1/reports/{filename}?{query}"

    @staticmethod
    def verify_signed_url(expires: int, token: str, filename: str):
        """
        Verifies signed url.

        Args:
            filename (str): The filename with .pdf or .docx extension
            expires_in (int): The period of expiration.
            token (str): The token to compare.
        """
        if not expires or not token:
            raise HTTPException(status_code=403, detail="Missing file report token")

        # Check expiry
        if expires < int(time.time()):
            raise HTTPException(status_code=403, detail="URL expired")

        # Validate signature
        data = f"{filename}:{expires}".encode()
        secret = (settings.url_secret).encode()
        expected_sig = hmac.new(secret, data, hashlib.sha256).digest()
        expected_token = base64.urlsafe_b64encode(expected_sig).decode().rstrip("=")

        if not hmac.compare_digest(token, expected_token):
            raise HTTPException(status_code=403, detail="Invalid file report token")
