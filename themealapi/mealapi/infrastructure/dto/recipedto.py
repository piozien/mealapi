"""A module containing recipe DTO model."""

from datetime import datetime
from typing import List, Optional, Dict
from pydantic import BaseModel, ConfigDict
from uuid import UUID
from mealapi.core.domain.rating import Rating
from mealapi.infrastructure.dto.commentdto import CommentDTO


class RecipeDTO(BaseModel):
    """A model representing DTO for recipe data."""
    id: int
    name: str
    description: Optional[str] = None
    instructions: str
    category: str
    ingredients: List[str] 
    preparation_time: int
    servings: Optional[int] = None
    difficulty: Optional[str] = None
    average_rating: Optional[float] = None
    ai_detected: Optional[float] = None
    author: UUID  
    created_at: datetime
    steps: List[str]
    tags: Optional[List[str]] = None
    comments: List[CommentDTO] = []

    model_config = ConfigDict(
        from_attributes=True,
        extra="ignore",
        arbitrary_types_allowed=True,
    )

    @classmethod
    def from_record(cls, record: Dict) -> "RecipeDTO":
        """A method for preparing DTO instance based on DB record.

        Args:
            record (Dict): The DB record.

        Returns:
            RecipeDTO: The final DTO instance.
        """
        # Converting comments to DTOs
        if 'comments' in record and record['comments']:
            comments = []
            for comment in record['comments']:
                rating = None
                if comment.get('rating_id') is not None and 'ratings' in record and record['ratings']:
                    for r in record['ratings']:
                        if r['id'] == comment['rating_id']:
                            rating = Rating(
                                id=r['id'],
                                value=r['value'],
                                recipe_id=r['recipe_id'],
                                author=r['author'],
                                created_at=r['created_at']
                            )
                            break
                
                comment_dto = CommentDTO(
                    id=comment['id'],
                    content=comment['content'],
                    recipe_id=comment['recipe_id'],
                    author=comment['author'],
                    created_at=comment['created_at'],
                    rating=rating
                )
                comments.append(comment_dto)
            record['comments'] = comments
        else:
            record['comments'] = []
            
        required_fields = {
            'id', 'name', 'instructions', 'category', 'ingredients',
            'preparation_time', 'author', 'created_at', 'steps'
        }
        missing_fields = required_fields - set(record.keys())
        if missing_fields:
            raise ValueError(f"Missing required fields: {missing_fields}")

        return cls(**record)
