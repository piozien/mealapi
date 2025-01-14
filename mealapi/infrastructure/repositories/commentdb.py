"""Module containing comment repository implementation."""

from typing import Any, Iterable, Dict
from sqlalchemy import select, and_
from datetime import datetime, timezone
from uuid import UUID

from mealapi.core.domain.comment import Comment, CommentIn
from mealapi.db import database
from mealapi.db import comment_table, rating_table, user_table


class InvalidCommentError(Exception):
    """Exception raised when a comment parameter is invalid."""


class CommentRepository:
    """A class representing comment DB repository."""

    async def get_by_recipe(self, recipe_id: int) -> Iterable[Any]:
        """Get all comments for a specific recipe.

        Args:
            recipe_id (int): The ID of the recipe

        Returns:
            Iterable[Any]: All comments for the recipe
        """
        query = (
            select(
                comment_table.c.id,
                comment_table.c.author,
                comment_table.c.recipe_id,
                comment_table.c.content,
                comment_table.c.rating_id,
                comment_table.c.created_at.label('created_at'),
                rating_table.c.id.label('rating_id'),
                rating_table.c.value,
                rating_table.c.recipe_id.label('rating_recipe_id'),
                rating_table.c.author.label('rating_author'),
                rating_table.c.created_at.label('rating_created_at'),
                user_table.c.email
            )
            .join(user_table, comment_table.c.author == user_table.c.id)
            .outerjoin(rating_table, and_(
                comment_table.c.rating_id == rating_table.c.id,
                rating_table.c.recipe_id == comment_table.c.recipe_id,
                rating_table.c.author == comment_table.c.author
            ))
            .where(comment_table.c.recipe_id == recipe_id)
        )
        result = await database.fetch_all(query)
        return [dict(row) for row in result]

    async def get_by_user(self, user_id: UUID) -> Iterable[Any]:
        """Get all comments made by a specific user.

        Args:
            user_id (UUID): The ID of the user

        Returns:
            Iterable[Any]: All comments made by the user
        """
        query = (
            select(
                comment_table.c.id,
                comment_table.c.author,
                comment_table.c.recipe_id,
                comment_table.c.content,
                comment_table.c.rating_id,
                comment_table.c.created_at.label('created_at'),
                rating_table.c.id.label('rating_id'),
                rating_table.c.value,
                rating_table.c.recipe_id.label('rating_recipe_id'),
                rating_table.c.author.label('rating_author'),
                rating_table.c.created_at.label('rating_created_at'),
                user_table.c.email
            )
            .join(user_table, comment_table.c.author == user_table.c.id)
            .outerjoin(rating_table, and_(
                comment_table.c.rating_id == rating_table.c.id,
                rating_table.c.recipe_id == comment_table.c.recipe_id,
                rating_table.c.author == comment_table.c.author
            ))
            .where(comment_table.c.author == user_id)
        )
        result = await database.fetch_all(query)
        return [dict(row) for row in result]

    async def get_by_id(self, comment_id: int) -> Dict | None:
        """Get a specific comment by its ID.

        Args:
            comment_id (int): The ID of the comment

        Returns:
            Dict | None: The comment if found
        """
        query = (
            select(
                comment_table.c.id,
                comment_table.c.author,
                comment_table.c.recipe_id,
                comment_table.c.content,
                comment_table.c.rating_id,
                comment_table.c.created_at,
                rating_table.c.id.label('rating_id'),
                rating_table.c.value,
                rating_table.c.recipe_id.label('rating_recipe_id'),
                rating_table.c.author.label('rating_author'),
                rating_table.c.created_at.label('rating_created_at'),
                user_table.c.email
            )
            .join(user_table, comment_table.c.author == user_table.c.id)
            .outerjoin(rating_table, and_(
                comment_table.c.rating_id == rating_table.c.id,
                rating_table.c.recipe_id == comment_table.c.recipe_id,
                rating_table.c.author == comment_table.c.author
            ))
            .where(comment_table.c.id == comment_id)
        )
        result = await database.fetch_one(query)
        return dict(result) if result else None

    async def get_rating_by_id(self, rating_id: int) -> Dict | None:
        """Get rating by its ID.

        Args:
            rating_id (int): The ID of the rating

        Returns:
            Dict | None: Rating data if found, None otherwise
        """
        query = (
            select(
                rating_table.c.id,
                rating_table.c.value,
                rating_table.c.recipe_id,
                rating_table.c.author,
                rating_table.c.created_at,
                user_table.c.email
            )
            .join(user_table, rating_table.c.author == user_table.c.id)
            .where(rating_table.c.id == rating_id)
        )
        result = await database.fetch_one(query)
        return dict(result) if result else None

    async def add_comment(self, comment: Comment, author: UUID) -> Dict | None:
        """Add a new comment to the database.

        Args:
            comment (Comment): The comment data.
            author (UUID): The author's UUID.

        Returns:
            Dict | None: The newly created comment, or None if failed.
        """
        try:
            async with database.transaction():
                # Create rating if provided
                rating_id = None
                
                if comment.rating and hasattr(comment.rating, 'value') and comment.rating.value is not None:
                    # Check if rating already exists for this user and recipe
                    query = select(rating_table).where(
                        and_(
                            rating_table.c.author == author,
                            rating_table.c.recipe_id == comment.recipe_id
                        )
                    )
                    existing_rating = await database.fetch_one(query)
                    
                    if existing_rating:
                        # Update existing rating
                        await database.execute(
                            rating_table.update()
                            .where(rating_table.c.id == existing_rating['id'])
                            .values(value=comment.rating.value)
                        )
                        rating_id = existing_rating['id']
                    else:
                        # Create new rating
                        rating_data = {
                            "author": author,
                            "recipe_id": comment.recipe_id,
                            "value": comment.rating.value,
                            "created_at": datetime.now(timezone.utc).replace(tzinfo=None)
                        }
                        rating_id = await database.execute(
                            rating_table.insert().values(**rating_data)
                        )

                # Create comment
                comment_data = {
                    "author": author,
                    "recipe_id": comment.recipe_id,
                    "content": comment.content,
                    "rating_id": rating_id,
                    "created_at": datetime.now(timezone.utc).replace(tzinfo=None)
                }
                comment_id = await database.execute(
                    comment_table.insert().values(**comment_data)
                )

                # Get created comment
                result = await self.get_by_id(comment_id)
                return result

        except Exception as e:
            raise InvalidCommentError(f"Could not create comment: {str(e)}")

    async def update_comment(self, comment_id: int, comment: CommentIn) -> Dict | None:
        """Update a comment's content and rating.

        Args:
            comment_id (int): The ID of the comment to update
            comment (CommentIn): The new comment data (content and rating)

        Returns:
            Dict | None: The updated comment

        Raises:
            InvalidCommentError: If comment data is invalid
        """
        try:
            existing_comment = await self.get_by_id(comment_id)
            if not existing_comment:
                return None

            async with database.transaction():
                # Update comment content
                update_data = {"content": comment.content}
                
                # Handle rating update
                if comment.rating is not None and comment.rating.value is not None:
                    if existing_comment["rating_id"] is not None:
                        # Update existing rating
                        await database.execute(
                            rating_table.update()
                            .where(rating_table.c.id == existing_comment["rating_id"])
                            .values(value=comment.rating.value)
                        )
                    else:
                        # Create new rating only if it didn't exist before
                        rating_data = {
                            "author": existing_comment["author"],
                            "recipe_id": existing_comment["recipe_id"],
                            "value": comment.rating.value,
                            "created_at": datetime.now(timezone.utc).replace(tzinfo=None)
                        }
                        rating_id = await database.execute(
                            rating_table.insert().values(**rating_data)
                        )
                        update_data["rating_id"] = rating_id
                elif comment.rating is None and existing_comment["rating_id"] is not None:
                    # Delete existing rating
                    await database.execute(
                        rating_table.delete()
                        .where(rating_table.c.id == existing_comment["rating_id"])
                    )
                    update_data["rating_id"] = None

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
            comment = await self.get_by_id(comment_id)
            if comment:
                async with database.transaction():
                    # Delete rating if exists
                    if comment.get("rating_id") is not None:
                        await database.execute(
                            rating_table.delete()
                            .where(rating_table.c.id == comment["rating_id"])
                        )

                    # Delete comment
                    await database.execute(
                        comment_table.delete()
                        .where(comment_table.c.id == comment_id)
                    )
                    return True
            return False
        except Exception as e:
            raise InvalidCommentError(f"Failed to delete comment: {str(e)}")
