"""
Abstract class module
"""

from abc import ABC, abstractmethod
import typing


class AbstractRepository(ABC):
    """
    Abstract Repository
    """

    @abstractmethod
    async def create(self, *args, **kwargs) -> typing.Any:
        """
        Create a new record
        """
        return

    @abstractmethod
    async def fetch(self, *args, **kwargs) -> typing.Any:
        """
        Ftehc a record
        """
        return

    @abstractmethod
    async def fetch_all(self, *args, **kwargs) -> typing.Any:
        """
        Fetch all  records
        """
        return

    @abstractmethod
    async def update(self, *args, **kwargs) -> typing.Any:
        """
        Update a record
        """
        return

    @abstractmethod
    async def delete(self, *args, **kwargs) -> typing.Any:
        """
        Delete a record
        """
        return
