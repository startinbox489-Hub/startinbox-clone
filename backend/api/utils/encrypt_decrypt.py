"""
Encrypt Decrypt Util
"""

import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend

from api.core.config import settings


class EncryptDecrypt:
    """
    EncryptDecrypt
    """

    @staticmethod
    def generate_key_from_secret() -> bytes:
        """
        Generate a secure encryption key from a secret string.

        Args:
            secret: The secret key string
            salt: Optional salt (generates random if not provided)

        Returns:
            bytes: Encryption key
        """

        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b"2b",
            iterations=100000,
            backend=default_backend(),
        )
        key = base64.urlsafe_b64encode(kdf.derive(settings.url_secret.encode()))
        return key

    @staticmethod
    def encrypt_value(value: str) -> str:
        """
        Encrypt a value using symmetric encryption.

        Args:
            value: The value to encrypt
            secret_key: The secret key for encryption

        Returns:
            str: Base64-encoded encrypted value
        """
        key = EncryptDecrypt.generate_key_from_secret()
        fernet = Fernet(key)
        encrypted = fernet.encrypt(value.encode())
        return base64.urlsafe_b64encode(encrypted).decode()

    @staticmethod
    def decrypt_value(encrypted_value: str) -> str:
        """
        Decrypt a value using symmetric encryption.

        Args:
            encrypted_value: The encrypted value to decrypt
            secret_key: The secret key for decryption

        Returns:
            str: Decrypted original value

        Raises:
            Exception: If decryption fails
        """
        key = EncryptDecrypt.generate_key_from_secret()
        fernet = Fernet(key)
        try:
            decrypted = fernet.decrypt(base64.urlsafe_b64decode(encrypted_value))
            return decrypted.decode()
        except Exception as e:
            raise RuntimeError(
                "Decryption failed - invalid key or corrupted data"
            ) from e
