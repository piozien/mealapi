"""Module containing comment data transfer objects."""
from datetime import datetime
from typing import Optional, Union
from uuid import UUID
from pydantic import BaseModel, ConfigDict
from databases.interfaces import Record
from mealapi.core.domain.rating import Rating


class CommentDTO(BaseModel):
    id: int
    author: UUID
    recipe_id: Optional[int] = None
    content: str
    rating: Optional[Rating] = None
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
        extra="ignore",
        arbitrary_types_allowed=True,
    )

    @classmethod
    def from_record(cls, record: Union[dict, Record]) -> "CommentDTO":
        """Create a CommentDTO from a database record.

        Args:
            record (dict | Record): The database record.

        Returns:
            CommentDTO: The created DTO.
        """
        if not isinstance(record, dict):
            record = dict(record)
            
        # Create rating object if rating data exists
        rating = None
        if record.get("value") is not None:
            rating = Rating.model_validate({
                "id": record["rating_id"],
                "value": record["value"],
                "recipe_id": record["rating_recipe_id"],
                "author": record["rating_author"],
                "created_at": record["rating_created_at"]
            })
            
        dto_data = {
            "id": record["id"],
            "author": record["author"],
            "recipe_id": record["recipe_id"],
            "content": record["content"],
            "created_at": record["created_at"],
            "rating": rating
        }
            
        return cls(**dto_data)
