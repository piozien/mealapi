"""Module containing comment repository abstractions."""

from abc import ABC, abstractmethod
from typing import Any, Iterable
from uuid import UUID
from mealapi.core.domain.comment import CommentCreate


class ICommentRepository(ABC):
    """An abstract class representing protocol of comment repository."""

    @abstractmethod
    async def get_by_recipe(self, recipe_id: int) -> Iterable[Any]:
        """Get all comments for a specific recipe.

        Args:
            recipe_id (int): The ID of the recipe

        Returns:
            Iterable[Any]: All comments for the recipe
        """

    @abstractmethod
    async def get_by_user(self, user_id: UUID) -> Iterable[Any]:
        """Get all comments made by a specific user.

        Args:
            user_id (UUID): The ID of the user

        Returns:
            Iterable[Any]: All comments made by the user
        """

    @abstractmethod
    async def get_by_id(self, comment_id: int) -> Any:
        """Get a specific comment by its ID.

        Args:
            comment_id (int): The ID of the comment

        Returns:
            Any: The comment if found
        """

    @abstractmethod
    async def add_comment(self, comment: CommentCreate) -> Any:
        """Add a new comment.

        Args:
            comment (CommentCreate): The comment to add

        Returns:
            Any: The newly created comment
        """

    @abstractmethod
    async def update_comment(self, comment_id: int, comment: CommentCreate) -> Any:
        """Update an existing comment.

        Args:
            comment_id (int): The ID of the comment to update
            comment (CommentCreate): The new comment data

        Returns:
            Any: The updated comment
        """

    @abstractmethod
    async def delete_comment(self, comment_id: int) -> bool:
        """Delete a comment.

        Args:
            comment_id (int): The ID of the comment to delete

        Returns:
            bool: True if deleted successfully
        """

    @abstractmethod
    async def get_rating_by_id(self, rating_id: int) -> Any:
        """Get rating by its ID.

        Args:
            rating_id (int): The ID of the rating

        Returns:
            Any: Rating data if found, None otherwise
        """
