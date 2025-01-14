"""Module containing rating domain models"""
from datetime import datetime, timezone
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field, model_validator


class RatingIn(BaseModel):
    """Model for rating input.

    Attributes:
        value: Rating value (1-5)
    """
    value: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)

    @model_validator(mode='after')
    def validate_rating(self) -> 'RatingIn':
        """Validate rating value.
        
        Returns:
            The validated rating model
            
        Raises:
            ValueError: If the rating value is invalid
        """
        if self.value is not None:
            if not isinstance(self.value, int):
                raise ValueError("Rating value must be an integer")
            if self.value < 1 or self.value > 5:
                raise ValueError("Rating value must be between 1 and 5")
        return self


class Rating(BaseModel):
    """Model representing rating attributes.

    Attributes:
        id: Unique identifier of the rating
        value: Rating value (1-5)
        recipe_id: ID of the recipe being rated
        author: UUID of the user who created the rating
        created_at: Timestamp when the rating was created
    """
    id: Optional[int] = Field(
        default=None,
        description="Unique identifier of the rating"
    )
    value: int
    recipe_id: int = Field(..., description="ID of the recipe being rated", gt=0)
    author: UUID = Field(..., description="UUID of the user who created the rating")
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Timestamp when the rating was created"
    )

    model_config = ConfigDict(from_attributes=True)

    @model_validator(mode='after')
    def validate_rating(self) -> 'Rating':
        """Validate rating value.
        
        Returns:
            The validated rating model
            
        Raises:
            ValueError: If the rating value is invalid
        """
        if not isinstance(self.value, int):
            raise ValueError("Rating value must be an integer")
        if self.value < 1 or self.value > 5:
            raise ValueError("Rating value must be between 1 and 5")
        return self
