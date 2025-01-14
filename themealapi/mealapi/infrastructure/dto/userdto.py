"""A module containing user DTO model."""

from pydantic import BaseModel, ConfigDict
from uuid import UUID
from mealapi.core.domain.user import UserRole


class UserDTO(BaseModel):
    """A DTO model for user."""

    id: UUID
    email: str
    role: UserRole

    model_config = ConfigDict(
        from_attributes=True,
        extra="ignore",
    )
