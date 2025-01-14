"""Module containing user data transfer objects.

This module defines the DTO (Data Transfer Object) models for users,
which are used to transfer user data between different layers of the application
and to format the response data sent to clients, excluding sensitive information.
"""

from pydantic import BaseModel, ConfigDict
from uuid import UUID
from mealapi.core.domain.user import UserRole


class UserDTO(BaseModel):
    """Data Transfer Object for users.
    
    This class represents the user data that is sent to clients in API responses.
    It includes essential user information while excluding sensitive data like passwords.
    
    Attributes:
        id (UUID): Unique identifier of the user
        email (str): User's email address
        role (UserRole): User's role in the system (ADMIN or USER)
    """
    id: UUID
    email: str
    role: UserRole

    model_config = ConfigDict(
        from_attributes=True,
        extra="ignore",
    )
