"""Module containing comment service implementations."""

from typing import Iterable
from uuid import UUID
from datetime import datetime, timezone
from fastapi import HTTPException

from mealapi.core.domain.comment import Comment, CommentIn, CommentCreate
from mealapi.core.repositories.icomment import ICommentRepository
from mealapi.infrastructure.services.icomment import ICommentService

class CommentService(ICommentService):
    """Comment service implementation."""

    def __init__(self, comment_repository: ICommentRepository):
        """The initializer of the comment service.

        Args:
            comment_repository (ICommentRepository): The comment repository.
        """
        self.comment_repository = comment_repository

    async def get_by_recipe(self, recipe_id: int) -> Iterable[Comment]:
        """Get all comments for a specific recipe.

        Args:   
            recipe_id (int): The ID of the recipe

        Returns:
            Iterable[Comment]: All comments for the recipe
        """
        return await self.comment_repository.get_by_recipe(recipe_id)

    async def get_by_user(self, user_id: UUID) -> Iterable[Comment]:
        """Get all comments made by a specific user.

        Args:
            user_id (UUID): The ID of the user

        Returns:
            Iterable[Comment]: All comments made by the user
        """
        return await self.comment_repository.get_by_user(user_id)

    async def get_by_id(self, comment_id: int) -> Comment | None:
        """Get a specific comment by its ID.

        Args:
            comment_id (int): The ID of the comment

        Returns:
            Comment | None: The comment if found, None otherwise
        """
        return await self.comment_repository.get_by_id(comment_id)

    async def add_comment(self, comment: Comment) -> Comment | None:
        """Add a new comment.

        Args:
            comment (Comment): The comment data to add

        Returns:
            Comment | None: The created comment or None if creation failed

        Raises:
            HTTPException: If comment creation fails
        """
        return await self.comment_repository.add_comment(comment, comment.author)

    async def update_comment(self, comment_id: int, comment: CommentIn) -> Comment | None:
        """Update an existing comment.

        Args:
            comment_id (int): The ID of the comment to update
            comment (CommentIn): The new comment data

        Returns:
            Comment | None: The updated comment
        """
        try:
            existing = await self.get_by_id(comment_id)
            if not existing:
                raise HTTPException(status_code=404, detail="Comment not found")

            return await self.comment_repository.update_comment(comment_id, comment)
        except HTTPException as he:
            raise he
        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=f"Could not update comment: {str(e)}"
            )

    async def delete_comment(self, comment_id: int, user_uuid: UUID) -> bool:
        """Delete a comment.

        Args:
            comment_id (int): The ID of the comment to delete
            user_uuid (UUID): The ID of the user attempting to delete the comment

        Returns:
            bool: True if the comment was deleted, False otherwise

        Raises:
            HTTPException: If the comment does not exist or user is not authorized
        """
        comment = await self.get_by_id(comment_id)
        if not comment:
            raise HTTPException(status_code=404, detail="Comment not found")

        if comment.author != user_uuid:
            raise HTTPException(
                status_code=403,
                detail="Not authorized to delete this comment"
            )

        return await self.comment_repository.delete_comment(comment_id)