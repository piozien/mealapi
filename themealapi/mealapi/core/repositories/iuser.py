"""Module containing user repository abstractions.

This module defines the interface for user repositories, specifying
the contract that any user repository implementation must fulfill.
The interface provides methods for managing user accounts in the
data storage, including registration and role management.
"""

from abc import ABC, abstractmethod
from typing import Any
from uuid import UUID

from mealapi.core.domain.user import UserIn, UserRole


class IUserRepository(ABC):
    """Abstract base class defining the user repository interface.
    
    This interface defines all operations that must be supported by
    any concrete user repository implementation. It provides methods
    for user registration, retrieval, and role management.
    """

    @abstractmethod
    async def register_user(self, user: UserIn) -> Any | None:
        """Register a new user in the system.

        Args:
            user (UserIn): User registration data including email and password

        Returns:
            Any | None: The created user if registration successful, None otherwise

        Note:
            The method should handle password hashing and validate
            that the email is not already registered.
        """

    @abstractmethod
    async def get_by_uuid(self, uuid: UUID) -> Any | None:
        """Retrieve a user by their UUID.

        Args:
            uuid (UUID): UUID of the user to retrieve

        Returns:
            Any | None: The user data if found, None otherwise

        Note:
            The returned user data should not include sensitive
            information like password hashes.
        """

    @abstractmethod
    async def get_by_email(self, email: str) -> Any | None:
        """Retrieve a user by their email address.

        Args:
            email (str): Email address of the user to retrieve

        Returns:
            Any | None: The user data if found, None otherwise

        Note:
            The email search should be case-insensitive and the
            returned data should not include sensitive information.
        """

    @abstractmethod
    async def update_role(self, user_id: UUID, role: UserRole) -> Any | None:
        """Update a user's role in the system.

        Args:
            user_id (UUID): ID of the user to update
            role (UserRole): New role for the user

        Returns:
            Any | None: The updated user data if successful, None otherwise

        Note:
            Only administrators should be able to update user roles.
            The method should validate the requester's permissions.
        """