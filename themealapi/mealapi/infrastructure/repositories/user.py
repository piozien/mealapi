"""A repository for user entity."""


from typing import Any

from uuid import UUID

from uuid_utils import uuid7

from mealapi.infrastructure.utils.password import hash_password
from mealapi.core.domain.user import UserIn
from mealapi.core.repositories.iuser import IUserRepository
from mealapi.db import database, user_table
from mealapi.core.domain.user import UserRole  


class UserRepository(IUserRepository):
    """An implementation of repository class for user."""

    async def register_user(self, user: UserIn) -> Any | None:
        """A method registering new user.

        Args:
            user (UserIn): The user input data.

        Returns:
            Any | None: The new user object.
        """

        if await self.get_by_email(user.email):
            return None

        user.password = hash_password(user.password)
        new_user_uuid = uuid7()
        query = user_table.insert().values(id=new_user_uuid, **user.model_dump())
        await database.execute(query)

        return await self.get_by_uuid(new_user_uuid)

    async def get_by_uuid(self, uuid: UUID) -> Any | None:
        """A method getting user by UUID.

        Args:
            uuid (UUID): UUID of the user.

        Returns:
            Any | None: The user object if exists.
        """
        query = user_table.select().where(user_table.c.id == uuid)
        return await database.fetch_one(query)

    async def get_by_email(self, email: str) -> Any | None:
        """A method getting user by email.

        Args:
            email (str): The email of the user.

        Returns:
            Any | None: The user object if exists.
        """
        query = user_table.select().where(user_table.c.email == email)
        return await database.fetch_one(query)

    async def update_role(self, user_id: UUID, role: UserRole) -> Any | None:
        """Update user's role.

        Args:
            user_id (UUID): The ID of the user
            role (UserRole): The new role to assign

        Returns:
            Any | None: The updated user if successful
        """
        query = (
            user_table
            .update()
            .where(user_table.c.id == user_id)
            .values(role=role)
            .returning(user_table)
        )
        return await database.fetch_one(query)
