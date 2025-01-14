"""Module containing recipe data transfer objects.

This module defines the DTO (Data Transfer Object) models for recipes,
which are used to transfer recipe data between different layers of the application
and to format the response data sent to clients, including associated comments and ratings.
"""

from datetime import datetime
from typing import List, Optional, Dict
from pydantic import BaseModel, ConfigDict
from uuid import UUID
from asyncpg import Record
from mealapi.core.domain.recipe import RecipeIn
from mealapi.core.domain.rating import Rating
from mealapi.infrastructure.dto.commentdto import CommentDTO


class RecipeDTO(BaseModel):
    """Data Transfer Object for recipes.
    
    This class represents the recipe data that is sent to clients in API responses.
    It includes all recipe information along with associated comments and ratings.
    
    Attributes:
        id (int): Unique identifier of the recipe
        name (str): Title of the recipe
        description (Optional[str]): Short description or introduction
        instructions (str): Detailed cooking instructions
        category (str): Recipe category (e.g., 'Dessert', 'Main Course')
        ingredients (List[str]): List of ingredients with amounts
        preparation_time (int): Time needed to prepare in minutes
        servings (Optional[int]): Number of servings
        difficulty (Optional[str]): Recipe difficulty level
        average_rating (Optional[float]): Average user rating (0.0-5.0)
        author (UUID): ID of the user who created the recipe
        created_at (datetime): Timestamp when the recipe was created
        steps (List[str]): Detailed preparation steps
        tags (Optional[List[str]]): Recipe tags for categorization
        comments (List[CommentDTO]): List of comments on the recipe
        ratings (List[Rating]): List of user ratings
        ai_detected (Optional[float]): AI content detection confidence score
    """
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
    author: UUID
    created_at: datetime
    steps: List[str]
    tags: Optional[List[str]] = None
    comments: List[CommentDTO] = []
    ratings: List[Rating] = []
    ai_detected: Optional[float] = None

    model_config = ConfigDict(
        from_attributes=True,
        extra="ignore",
        arbitrary_types_allowed=True,
    )

    @classmethod
    def from_record(cls, record: Dict) -> "RecipeDTO":
        """Create a RecipeDTO from a database record.

        This method handles the conversion of database records into RecipeDTO instances,
        including the processing of nested comments and ratings data.

        Args:
            record (Dict): Database record containing recipe data and related entities

        Returns:
            RecipeDTO: A new RecipeDTO instance containing the recipe data and its relations

        Example:
            >>> record = {
            ...     "id": 1,
            ...     "name": "Chocolate Cake",
            ...     "instructions": "Mix and bake...",
            ...     "author": UUID("550e8400-e29b-41d4-a716-446655440000"),
            ...     "comments": [{"id": 1, "content": "Great recipe!"}],
            ...     "ratings": [{"id": 1, "value": 5}]
            ... }
            >>> recipe_dto = RecipeDTO.from_record(record)
        """
        # Convert comments to DTOs if present
        if 'comments' in record and record['comments']:
            record['comments'] = [
                CommentDTO.from_record(comment) if isinstance(comment, dict) else comment
                for comment in record['comments']
            ]

        # Convert ratings to Rating objects if present
        if 'ratings' in record and record['ratings']:
            record['ratings'] = [
                Rating(**rating) if isinstance(rating, dict) else rating
                for rating in record['ratings']
            ]

        return cls(**record)
