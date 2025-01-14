"""Module containing comment validation utilities."""

from datetime import datetime, timezone
from typing import Optional
from uuid import UUID
from mealapi.core.domain.comment import Comment


class CommentValidator:
    """A class for validating comment-related data."""

    @staticmethod
    def validate_content(content: str) -> str:
        """Validate comment content.

        Args:
            content (str): Comment text

        Returns:
            str: Validated content

        Raises:
            ValueError: If content is invalid
        """
        if not content:
            raise ValueError("Comment content cannot be empty")

        if len(content) > 1000:
            raise ValueError("Comment content cannot exceed 1000 characters")

        return content

    @staticmethod
    def validate_rating(rating: Optional[int]) -> Optional[int]:
        """Validate rating value.

        Args:
            rating (Optional[int]): Rating value

        Returns:
            Optional[int]: Validated rating

        Raises:
            ValueError: If rating is invalid
        """
        if rating is None:
            return None

        if not isinstance(rating, int):
            raise ValueError("Rating must be an integer")

        if rating < 1 or rating > 5:
            raise ValueError("Rating must be between 1 and 5")

        return rating

    @staticmethod
    def validate_author(author: UUID) -> UUID:
        """Validate comment author.

        Args:
            author (UUID): Author's unique identifier

        Returns:
            UUID: Validated author

        Raises:
            ValueError: If author is invalid
        """
        if author is None:
            raise ValueError("Author cannot be None")

        return author

    @staticmethod
    def validate_recipe_id(recipe_id: int) -> int:
        """Validate recipe identifier.

        Args:
            recipe_id (int): Recipe's unique identifier

        Returns:
            int: Validated recipe ID

        Raises:
            ValueError: If recipe_id is invalid
        """
        if not isinstance(recipe_id, int):
            raise ValueError("Recipe ID must be an integer")

        if recipe_id <= 0:
            raise ValueError("Recipe ID must be a positive integer")

        return recipe_id

    @staticmethod
    def ensure_utc_timezone(dt: datetime) -> datetime:
        """Ensure the datetime has UTC timezone.

        Args:
            dt (datetime): Input datetime

        Returns:
            datetime: Datetime with UTC timezone
        """
        if dt.tzinfo is None:
            return dt.replace(tzinfo=timezone.utc)
        return dt

    @classmethod
    def validate(cls, comment: Comment) -> None:
        """Validate the entire comment object.

        Args:
            comment (Comment): Comment object to validate

        Raises:
            ValueError: If any comment attribute is invalid
        """
        # Validate the recipe ID
        cls.validate_recipe_id(comment.recipe_id)

        # Validate the content
        cls.validate_content(comment.content)

        # Validatse the rating if provided
        if comment.rating is not None:
            cls.validate_rating(comment.rating)

        # Validate the author
        cls.validate_author(comment.author)

        # Ensure `created_at` is UTC timezone-naive
        if hasattr(comment, 'created_at') and comment.created_at:
            comment.created_at = cls.ensure_utc_timezone(comment.created_at)
