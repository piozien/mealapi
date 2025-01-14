"""Module containing comment repository abstractions.

This module defines the interface for comment repositories, specifying
the contract that any comment repository implementation must fulfill.
The interface provides methods for managing comments in the data storage.
"""

from abc import ABC, abstractmethod
from typing import Any, Iterable, Dict
from uuid import UUID
from mealapi.core.domain.comment import Comment, CommentIn, CommentCreate


class ICommentRepository(ABC):
    """Abstract base class defining the comment repository interface.
    
    This interface defines all operations that must be supported by
    any concrete comment repository implementation. It provides methods
    for retrieving, creating, updating, and deleting comments.
    """

    @abstractmethod
    async def get_by_recipe(self, recipe_id: int) -> Iterable[Any]:
        """Retrieve all comments for a specific recipe.

        Args:
            recipe_id (int): ID of the recipe to get comments for

        Returns:
            Iterable[Any]: Collection of comments associated with the recipe

        Note:
            The returned comments should include all related data like
            author information and creation timestamps.
        """

    @abstractmethod
    async def get_by_user(self, user_id: UUID) -> Iterable[Any]:
        """Retrieve all comments made by a specific user.

        Args:
            user_id (UUID): ID of the user to get comments for

        Returns:
            Iterable[Any]: Collection of comments made by the user

        Note:
            The returned comments should be ordered by creation date,
            with the most recent comments first.
        """

    @abstractmethod
    async def get_by_id(self, comment_id: int) -> Any:
        """Retrieve a specific comment by its ID.

        Args:
            comment_id (int): ID of the comment to retrieve

        Returns:
            Any: The comment data if found, None otherwise

        Note:
            The returned comment should include all related data
            including author information and any associated rating.
        """

    @abstractmethod
    async def add_comment(self, comment: CommentCreate) -> Any:
        """Create a new comment.

        Args:
            comment (CommentCreate): Comment data to create

        Returns:
            Any: The created comment with generated ID and metadata

        Note:
            The method should handle setting the creation timestamp
            and validating the comment content.
        """

    @abstractmethod
    async def update_comment(self, comment_id: int, comment: CommentIn) -> Any:
        """Update an existing comment.

        Args:
            comment_id (int): ID of the comment to update
            comment (CommentIn): New comment data

        Returns:
            Any: The updated comment data

        Note:
            Only the comment content and optional rating should be
            updatable. Other fields like author and creation date
            should remain unchanged.
        """

    @abstractmethod
    async def delete_comment(self, comment_id: int) -> bool:
        """Delete a comment.

        Args:
            comment_id (int): ID of the comment to delete

        Returns:
            bool: True if comment was deleted, False if not found

        Note:
            This operation should also handle cleanup of any related
            data such as associated ratings or reports.
        """