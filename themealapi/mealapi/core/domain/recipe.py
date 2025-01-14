"""Module containing recipe domain models.

This module defines the core data models for recipes in the application.
Recipes are the central entity that users can create, rate, and comment on.
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict
from uuid import UUID


class RecipeIn(BaseModel):
    """Base model for recipe attributes used when creating or updating a recipe.
    
    Attributes:
        name (str): Title of the recipe
        description (Optional[str]): Short description or introduction to the recipe
        instructions (str): Detailed step-by-step cooking instructions
        category (str): Recipe category (e.g., 'Dessert', 'Main Course')
        ingredients (List[str]): List of ingredients in format "amount:ingredient"
        preparation_time (int): Estimated preparation time in minutes
        servings (Optional[int]): Number of servings the recipe yields
        difficulty (Optional[str]): Recipe difficulty level (e.g., 'Easy', 'Medium', 'Hard')
        steps (Optional[List[str]]): Detailed list of preparation steps
        tags (Optional[List[str]]): Keywords for recipe categorization and search
    """
    name: str
    description: Optional[str] = None
    instructions: str
    category: str
    ingredients: List[str]
    preparation_time: int
    servings: Optional[int] = None
    difficulty: Optional[str] = None
    steps: Optional[List[str]] = None
    tags: Optional[List[str]] = None


class Recipe(RecipeIn):
    """Model representing a complete recipe in the database.
    
    Extends RecipeIn to include additional fields for database storage and recipe metadata.
    
    Attributes:
        id (Optional[int]): Unique identifier of the recipe
        author (UUID): ID of the user who created the recipe
        created_at (Optional[datetime]): Timestamp when the recipe was created
        average_rating (float): Average rating from all user ratings (0.0-5.0)
        ai_detected (Optional[float]): Confidence score if AI-generated content was detected
    """
    id: Optional[int] = None
    author: UUID
    created_at: Optional[datetime] = None
    average_rating: float = 0.0
    ai_detected: Optional[float] = None
    model_config = ConfigDict(from_attributes=True, extra="ignore")