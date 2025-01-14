"""A repository for user entity."""


from abc import ABC, abstractmethod
from typing import Any

from uuid import UUID

from mealapi.core.domain.user import UserIn, UserRole


class IUserRepository(ABC):
    """An abstract repository class for user."""

    @abstractmethod
    async def register_user(self, user: UserIn) -> Any | None:
        """A method registering new user.

        Args:
            user (UserIn): The user input data.

        Returns:
            Any | None: The new user object.
        """

    @abstractmethod
    async def get_by_uuid(self, uuid: UUID) -> Any | None:
        """A method getting user by UUID.

        Args:
            uuid (UUID): UUID of the user.

        Returns:
            Any | None: The user object if exists.
        """

    @abstractmethod
    async def get_by_email(self, email: str) -> Any | None:
        """A method getting user by email.

        Args:
            email (str): The email of the user.

        Returns:
            Any | None: The user object if exists.
        """

    @abstractmethod
    async def update_role(self, user_id: UUID, role: UserRole) -> Any | None:
        """Update user's role.
    
        Args:
            user_id (UUID): The ID of the user
            role (UserRole): The new role to assign
    
        Returns:
            Any | None: The updated user if successful
        """