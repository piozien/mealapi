"""Module containing comment data transfer objects.

This module defines the DTO (Data Transfer Object) models for comments,
which are used to transfer comment data between different layers of the application
and to format the response data sent to clients.
"""

from datetime import datetime
from typing import Optional, Union
from uuid import UUID
from pydantic import BaseModel, ConfigDict
from mealapi.infrastructure.utils.comment_validator import CommentValidator
from databases.interfaces import Record


class CommentDTO(BaseModel):
    """Data Transfer Object for comments.
    
    This class represents the comment data that is sent to clients in API responses.
    It includes all necessary comment information while excluding sensitive or internal data.
    
    Attributes:
        id (int): Unique identifier of the comment
        author (UUID): ID of the user who created the comment
        recipe_id (int): ID of the recipe this comment belongs to
        content (str): The text content of the comment
        rating_id (Optional[int]): ID of the associated rating, if any
        created_at (datetime): Timestamp when the comment was created
    """
    id: int
    author: UUID
    recipe_id: int
    content: str
    rating_id: Optional[int] = None
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
        extra="ignore",
        arbitrary_types_allowed=True,
    )

    @classmethod
    def from_record(cls, record: Union[dict, Record]) -> "CommentDTO":
        """Create a CommentDTO from a database record.

        This method handles the conversion of database records (either as dict or Record objects)
        into CommentDTO instances, ensuring all required fields are properly mapped.

        Args:
            record (Union[dict, Record]): Database record containing comment data

        Returns:
            CommentDTO: A new CommentDTO instance containing the comment data

        Example:
            >>> record = {
            ...     "id": 1,
            ...     "author": UUID("550e8400-e29b-41d4-a716-446655440000"),
            ...     "recipe_id": 123,
            ...     "content": "Great recipe!",
            ...     "rating_id": 456,
            ...     "created_at": datetime.now()
            ... }
            >>> comment_dto = CommentDTO.from_record(record)
        """
        if not isinstance(record, dict):
            record = dict(record)
            
        dto_data = {
            "id": record["id"],
            "author": record["author"],
            "recipe_id": record["recipe_id"],
            "content": record["content"],
            "created_at": record["created_at"]
        }
        
        if record.get("rating_id") is not None:
            dto_data["rating_id"] = record["rating_id"]
            
        return cls(**dto_data)
