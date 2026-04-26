"""
Exception classes
"""


class CustomMetaException(Exception):
    """
    CustomMetaException
    """

    def __init__(self, message: str = "Error sending files to whatsapp") -> None:
        """
        Constructor
        """
        super().__init__(message)
