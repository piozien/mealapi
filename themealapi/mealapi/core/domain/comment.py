"""Module containing comments domain model"""
from datetime import datetime, timezone
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field
from mealapi.core.domain.rating import Rating, RatingIn


class CommentBase(BaseModel):
    """Base model for comment with common fields"""
    content: str = Field(..., description="Comment content", min_length=1, max_length=500)

    model_config = ConfigDict(from_attributes=True)


class CommentIn(BaseModel):
    """Model representing comment input attributes for creation and updating"""
    content: str = Field(..., description="Comment content", min_length=1, max_length=500)
    recipe_id: Optional[int] = Field(None, description="ID of the recipe", gt=0)
    rating: Optional[RatingIn] = Field(
        default=None,
        description="Optional rating for the comment"
    )

    model_config = ConfigDict(from_attributes=True)


class CommentCreate(CommentBase):
    """Model representing comment input attributes for creation"""
    recipe_id: int = Field(..., description="ID of the recipe", examples=[1])
    rating: Optional[RatingIn] = Field(default=None)

    @classmethod
    def validate_recipe_id(cls, v: int) -> int:
        """Validate that recipe_id is greater than 0"""
        if v <= 0:
            raise ValueError("Recipe ID must be greater than 0")
        return v


class Comment(CommentBase):
    """Model representing comment attributes in the database"""
    id: Optional[int] = Field(default=None)
    author: UUID
    recipe_id: int
    rating: Optional[Rating] = Field(default=None)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    model_config = ConfigDict(from_attributes=True)
