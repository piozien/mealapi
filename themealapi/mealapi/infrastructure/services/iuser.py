"""A module containing user service interface."""


from abc import ABC, abstractmethod
from typing import Optional

from uuid import UUID

from pydantic import BaseModel

from mealapi.core.domain.user import UserIn, UserRole
from mealapi.infrastructure.dto.userdto import UserDTO
from mealapi.infrastructure.dto.tokendto import TokenDTO


class IUserService(ABC):
    """An abstract class for user service."""

    @abstractmethod
    async def register_user(self, user: UserIn) -> UserDTO | None:
        """A method registering a new user.

        Args:
            user (UserIn): The user input data.

        Returns:
            UserDTO | None: The user DTO model.
        """

    @abstractmethod
    async def authenticate_user(self, user: UserIn) -> TokenDTO | None:
        """The method authenticating the user.

        Args:
            user (UserIn): The user data.

        Returns:
            TokenDTO | None: The token details.
        """

    @abstractmethod
    async def get_by_uuid(self, uuid: UUID) -> UserDTO | None:
        """A method getting user by UUID.

        Args:
            uuid (UUID): The UUID of the user.

        Returns:
            UserDTO | None: The user data, if found.
        """

    @abstractmethod
    async def update_role(self, user_id: UUID, role: UserRole) -> UserDTO | None:
        """Update user's role.

        Args:
            user_id (UUID): The ID of the user
            role (UserRole): The new role to assign

        Returns:
            UserDTO | None: The updated user if successful
        """