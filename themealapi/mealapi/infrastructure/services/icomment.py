"""Module containing comment service abstractions."""

from abc import ABC, abstractmethod
from typing import Iterable

from uuid import UUID
from mealapi.core.domain.comment import Comment, CommentIn
from mealapi.infrastructure.dto.commentdto import CommentDTO

class ICommentService(ABC):
    """An abstract class representing protocol of comment service."""

    @abstractmethod
    async def get_by_recipe(self, recipe_id: int) -> Iterable[Comment]:
        """Get all comments for a specific recipe.

        Args:
            recipe_id (int): The ID of the recipe

        Returns:
            Iterable[Comment]: All comments for the recipe
        """
    @abstractmethod
    async def get_by_user(self, user_id: UUID) -> Iterable[Comment]:
        """Get all comments made by a specific user.

        Args:
            user_id (UUID): The ID of the user

        Returns:
            Iterable[Comment]: All comments made by the user
        """

    @abstractmethod
    async def get_by_id(self, comment_id: int) -> Comment:
        """Get a specific comment by its ID.

        Args:
            comment_id (int): The ID of the comment

        Returns:
            Comment: The comment if found
        """

    @abstractmethod
    async def add_comment(self, comment: CommentIn) -> CommentDTO | None:
        """Add a new comment.

        Args:
            comment (CommentIn): The comment to add

        Returns:
            CommentDTO | None: The newly created comment
        """
        

    @abstractmethod
    async def update_comment(self, comment_id: int, comment: CommentIn) -> Comment | None:
        """Update an existing comment.

        Args:
            comment_id (int): The ID of the comment to update
            comment (CommentIn): The new comment data

        Returns:
            Comment | None: The updated comment
        """

    @abstractmethod
    async def delete_comment(self, comment_id: int) -> bool:
        """Delete a comment.

        Args:
            comment_id (int): The ID of the comment to delete

        Returns:
            bool: True if deleted successfully
        """
