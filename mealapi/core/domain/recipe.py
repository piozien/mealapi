"""Module containing recipe domain models"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict, field_validator, Field
from uuid import UUID
import unicodedata


class RecipeIn(BaseModel):
    """Base model for recipe attributes"""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    instructions: str = Field(..., min_length=1, max_length=2000)
    category: str = Field(..., min_length=1, max_length=50)
    ingredients: List[str] = Field(..., description="List of ingredients in format 'amount:ingredient'")
    preparation_time: int = Field(..., gt=0, le=1440)  # 24 hours
    servings: Optional[int] = Field(None, gt=0, le=100)
    difficulty: Optional[str] = Field(None, pattern="^(easy|medium|hard|łatwy|średni|trudny)$")
    steps: Optional[List[str]] = Field(None, max_length=50)
    tags: Optional[List[str]] = Field(None, max_length=20)
    model_config = ConfigDict(from_attributes=True)

    @field_validator('ingredients')
    @classmethod
    def validate_ingredients(cls, v: List[str]) -> List[str]:
        """Validate and normalize ingredients format."""
        normalized = []
        for ingredient in v:
            # Check format
            if ':' not in ingredient:
                raise ValueError(f"Invalid ingredient format: {ingredient}. Must be 'amount:ingredient'")

            amount, name = ingredient.split(':', 1)
            if not amount or not name:
                raise ValueError(f"Invalid ingredient format: {ingredient}. Both amount and name must be non-empty")

            # Normalize
            normalized.append(f"{amount.strip()}:{name.strip().lower()}")
        return normalized

    @field_validator('tags')
    @classmethod
    def validate_tags(cls, v: Optional[List[str]]) -> Optional[List[str]]:
        """Validate and normalize tags."""
        if v is None:
            return v

        normalized = []
        for tag in v:
            if not tag:
                raise ValueError("Tags cannot be empty")
            # Remove diacritics and convert to lowercase
            normalized_tag = ''.join(
                char for char in unicodedata.normalize('NFKD', tag.lower())
                if unicodedata.category(char) != 'Mn'
            )
            normalized.append(normalized_tag)
        return normalized

    @field_validator('steps')
    @classmethod
    def validate_steps(cls, v: Optional[List[str]]) -> Optional[List[str]]:
        """Validate recipe steps."""
        if v is None:
            return v

        for step in v:
            if not step:
                raise ValueError("Steps cannot be empty")
            if len(step) > 500:
                raise ValueError("Step description cannot exceed 500 characters")
        return v


class Recipe(RecipeIn):
    """Model representing a complete recipe"""
    id: Optional[int] = None
    author: UUID
    created_at: Optional[datetime] = None
    average_rating: float = Field(default=0.0, ge=0, le=5)
    model_config = ConfigDict(from_attributes=True, extra="ignore")
