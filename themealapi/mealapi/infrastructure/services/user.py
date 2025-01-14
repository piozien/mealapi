"""A module containing user service implementation."""

from uuid import UUID
from fastapi import HTTPException
from pydantic import BaseModel

from mealapi.core.domain.user import UserIn, UserRole
from mealapi.core.repositories.iuser import IUserRepository
from mealapi.infrastructure.dto.userdto import UserDTO
from mealapi.infrastructure.dto.tokendto import TokenDTO
from mealapi.infrastructure.services.iuser import IUserService
from mealapi.infrastructure.utils.password import verify_password
from mealapi.infrastructure.utils.token import generate_user_token


class UserService(IUserService):
    """An abstract class for user service."""

    _repository: IUserRepository

    def __init__(self, repository: IUserRepository) -> None:
        self._repository = repository

    async def register_user(self, user: UserIn) -> UserDTO | None:
        """A method registering a new user.

        Args:
            user (UserIn): The user input data.

        Returns:
            UserDTO | None: The user DTO model.
        """
        if user_data := await self._repository.register_user(user):
            return UserDTO.from_orm(user_data)
        return None

    async def authenticate_user(self, user: UserIn) -> TokenDTO | None:
        """The method authenticating the user.

        Args:
            user (UserIn): The user data.

        Returns:
            TokenDTO | None: The token details.

        Raises:
            HTTPException: If role in request doesn't match role in database
        """
        if user_data := await self._repository.get_by_email(user.email):
            if verify_password(user.password, user_data.password):
                if hasattr(user, 'role') and user.role != user_data.role:
                    raise HTTPException(
                        status_code=401,
                        detail=f"Provided role '{user.role}' doesn't match registered role '{user_data.role}'"
                    )
                token_details = generate_user_token(user_data.id, user_data.role)
                return TokenDTO(token_type="Bearer", **token_details)

        return None

    async def get_by_uuid(self, uuid: UUID) -> UserDTO | None:
        """A method getting user by UUID.

        Args:
            uuid (UUID): The UUID of the user.

        Returns:
            UserDTO | None: The user data, if found.
        """
        if user_data := await self._repository.get_by_uuid(uuid):
            return UserDTO.from_orm(user_data)
        return None

    async def update_role(self, user_id: UUID, role: UserRole) -> UserDTO | None:
        """Update user's role.

        Args:
            user_id (UUID): The ID of the user
            role (UserRole): The new role to assign

        Returns:
            UserDTO | None: The updated user if successful
        """
        if updated_user := await self._repository.update_role(user_id, role):
            return UserDTO.from_orm(updated_user)
        return None
