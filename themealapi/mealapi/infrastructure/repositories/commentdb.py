"""Module containing comment repository implementation."""

from typing import Any, Iterable, Dict
from sqlalchemy import select
from sqlalchemy.engine import Row as Record
from datetime import datetime, timezone

from uuid import UUID

from mealapi.core.repositories.icomment import ICommentRepository
from mealapi.core.domain.comment import CommentIn, Comment, CommentCreate
from mealapi.infrastructure.dto.commentdto import CommentDTO
from mealapi.db import comment_table, rating_table, user_table, recipe_table, database
from mealapi.infrastructure.utils.comment_validator import CommentValidator
from mealapi.infrastructure.utils.recipe_mapper import RecipeMapper

class InvalidCommentError(Exception):
    """Exception raised when a comment parameter is invalid."""
    pass


class CommentRepository(ICommentRepository):
    """A class representing comment DB repository."""

    async def get_by_recipe(self, recipe_id: int) -> Iterable[Any]:
        """Get all comments for a specific recipe.

        Args:
            recipe_id (int): The ID of the recipe

        Returns:
            Iterable[Any]: All comments for the recipe
        """
        query = (
            select(comment_table, rating_table, user_table.c.email)
            .outerjoin(rating_table, comment_table.c.rating_id == rating_table.c.id)
            .join(user_table, comment_table.c.author == user_table.c.id)
            .where(comment_table.c.recipe_id == recipe_id)
            .order_by(comment_table.c.id.asc())
        )
        comments = await database.fetch_all(query)
        return [CommentDTO.from_record(comment) for comment in comments]

    async def get_by_user(self, user_id: UUID) -> Iterable[Any]:
        """Get all comments made by a specific user.

        Args:
            user_id (UUID): The ID of the user

        Returns:
            Iterable[Any]: All comments made by the user
        """
        query = (
            select(comment_table, rating_table, user_table.c.email)
            .outerjoin(rating_table, comment_table.c.rating_id == rating_table.c.id)
            .outerjoin(user_table, comment_table.c.author == user_table.c.id)
            .where(comment_table.c.author == user_id)
            .order_by(comment_table.c.created_at.desc())
        )
        comments = await database.fetch_all(query)
        return [CommentDTO.from_record(comment) for comment in comments]

    async def get_by_id(self, comment_id: int) -> Any | None:
        """Get a specific comment by its ID.

        Args:
            comment_id (int): The ID of the comment

        Returns:
            Any | None: The comment if found
        """
        query = (
            select(comment_table, rating_table, user_table.c.email)
            .outerjoin(rating_table, comment_table.c.rating_id == rating_table.c.id)
            .join(user_table, comment_table.c.author == user_table.c.id)
            .where(comment_table.c.id == comment_id)
        )
        comment = await database.fetch_one(query)
        
        if comment:
            comment_dict = dict(comment)
            # Ensure created_at is timezone-aware
            if comment_dict.get('created_at') and comment_dict['created_at'].tzinfo is None:
                comment_dict['created_at'] = comment_dict['created_at'].replace(tzinfo=timezone.utc)
            
            return CommentDTO.from_record(comment_dict)
        return None

    async def add_comment(self, comment: Comment, author: UUID) -> Any | None:
        """Add a new comment to the database.

        Args:
            comment (Comment): The comment data.
            author (UUID): The author's UUID.

        Returns:
            Any | None: The newly created comment, or None if failed.
        """
        try:
            # Validate comment data
            CommentValidator.validate(comment)

            async with database.transaction():
                # Ensure `created_at` is set
                comment.created_at = datetime.now(timezone.utc).replace(tzinfo=None)

                # Prepare rating data if rating is provided
                rating_id = None
                if comment.rating is not None:
                    rating_data = {
                        "author": author,
                        "recipe_id": comment.recipe_id,
                        "value": comment.rating,
                        "created_at": comment.created_at,
                    }
                    rating_query = rating_table.insert().values(**rating_data)
                    rating_id = await database.execute(rating_query)

                # Prepare comment data
                comment_data = {
                    "recipe_id": comment.recipe_id,
                    "content": comment.content,
                    "author": author,
                    "created_at": comment.created_at,
                }
                if rating_id is not None:
                    comment_data["rating_id"] = rating_id

                # Save comment to the database
                comment_query = comment_table.insert().values(**comment_data)
                comment_id = await database.execute(comment_query)

                # Retrieve and return the newly created comment
                return await self.get_by_id(comment_id)

        except Exception as e:
            raise Exception(f"Could not create comment: {str(e)}")

    async def update_comment(self, comment_id: int, comment: CommentIn) -> Any | None:
        """Update a comment's content and rating.

        Args:
            comment_id (int): The ID of the comment to update
            comment (CommentIn): The new comment data (content and rating)

        Returns:
            Any | None: The updated comment

        Raises:
            InvalidCommentError: If comment data is invalid
        """
        try:
            existing_comment = await self._get_by_id(comment_id)
            if not existing_comment:
                return None

            async with database.transaction():
                # Update comment content
                update_data = {"content": comment.content}
                if comment.rating is not None:
                    # If rating changed, create new rating
                    rating_data = {
                        "author": existing_comment["author"],
                        "recipe_id": existing_comment["recipe_id"],
                        "value": comment.rating,
                        "created_at": datetime.now(timezone.utc).replace(tzinfo=None)
                    }
                    rating_id = await database.execute(
                        rating_table.insert().values(**rating_data)
                    )
                    update_data["rating_id"] = rating_id

                # Update comment
                await database.execute(
                    comment_table.update()
                    .where(comment_table.c.id == comment_id)
                    .values(**update_data)
                )

                # Get updated comment
                return await self.get_by_id(comment_id)

        except Exception as e:
            raise InvalidCommentError(f"Failed to update comment: {str(e)}")

    async def delete_comment(self, comment_id: int) -> bool:
        """Delete a comment.

        Args:
            comment_id (int): The ID of the comment to delete

        Returns:
            bool: True if comment was deleted, False if comment was not found
        """
        try:
            comment = await self._get_by_id(comment_id)
            if comment:
                query = comment_table.delete().where(comment_table.c.id == comment_id)
                await database.execute(query)
                return True
            return False
        except Exception as e:
            raise InvalidCommentError(f"Failed to delete comment: {str(e)}")

    async def _get_by_id(self, comment_id: int) -> Dict | None:
        """Get a comment record by ID.

        Args:
            comment_id (int): The ID of the comment

        Returns:
            Dict | None: The comment record if found
        """
        query = (
            select(
                comment_table.c.id,
                comment_table.c.author,
                comment_table.c.recipe_id,
                comment_table.c.content,
                comment_table.c.rating_id,
                comment_table.c.created_at,
                rating_table.c.value,
                user_table.c.email
            )
            .outerjoin(rating_table, comment_table.c.rating_id == rating_table.c.id)
            .join(user_table, comment_table.c.author == user_table.c.id)
            .where(comment_table.c.id == comment_id)
        )
        result = await database.fetch_one(query)
        if result:
            return dict(result)
        return None

    def _validate_comment(self, comment: CommentIn) -> None:
        """Validate comment data before insertion.

        Args:
            comment (CommentIn): Comment to validate

        Raises:
            InvalidCommentError: If comment is invalid
        """
        try:
            CommentValidator.validate_content(comment.content)
            if comment.rating is not None:
                CommentValidator.validate_rating(comment.rating)
        except ValueError as e:
            raise InvalidCommentError(str(e))