"""Module containing comment domain models.

This module defines the data models for handling comments in the recipe application.
Comments can be associated with recipes and optionally with ratings.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict


class CommentIn(BaseModel):
    """Model representing comment input attributes for updating an existing comment.
    
    Attributes:
        content (str): The text content of the comment
        rating (Optional[int]): Optional rating value (1-5) associated with the comment
    """
    content: str
    rating: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)


class CommentCreate(BaseModel):
    """Model representing comment input attributes for creating a new comment.
    
    Attributes:
        recipe_id (int): ID of the recipe this comment is associated with
        content (str): The text content of the comment
        rating (Optional[int]): Optional rating value (1-5) for the recipe
    """
    recipe_id: int
    content: str
    rating: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)


class Comment(CommentCreate):
    """Model representing comment attributes in the database.
    
    Extends CommentCreate to include additional fields for database storage.
    
    Attributes:
        author (UUID): ID of the user who created the comment
        created_at (datetime): Timestamp when the comment was created
        rating_id (Optional[int]): ID of the associated rating if one exists
        id (Optional[int]): Unique identifier of the comment
    """
    author: UUID
    created_at: datetime
    rating_id: Optional[int] = None
    id: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)
