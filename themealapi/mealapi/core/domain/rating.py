"""Module containing rating domain models.

This module defines the data models for handling recipe ratings in the application.
Ratings are numerical values (1-5) that users can assign to recipes.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict


class RatingIn(BaseModel):
    """Model for creating a new rating.
    
    Attributes:
        value (int): Rating value from 1 to 5
        recipe_id (int): ID of the recipe being rated
        author (UUID): ID of the user creating the rating
    """
    value: int
    recipe_id: int
    author: UUID


class Rating(RatingIn):
    """Model representing a complete rating in the database.
    
    Extends RatingIn to include additional fields for database storage.
    
    Attributes:
        id (Optional[int]): Unique identifier of the rating
        created_at (Optional[datetime]): Timestamp when the rating was created
    """
    id: Optional[int] = None
    created_at: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True, extra="ignore")
