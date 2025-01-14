"""Module containing comment service implementations."""

from typing import Dict, List, Optional
from uuid import UUID
from datetime import datetime, timezone
from fastapi import HTTPException
from pydantic import ValidationError

from mealapi.core.domain.comment import Comment, CommentIn, CommentCreate
from mealapi.core.domain.rating import Rating
from mealapi.core.repositories.icomment import ICommentRepository
from mealapi.infrastructure.services.icomment import ICommentService
from mealapi.infrastructure.services.iuser import IUserService


class CommentService(ICommentService):
    """Comment service implementation."""

    def __init__(self, comment_repository: ICommentRepository, user_service: IUserService):
        """Initialize comment service.

        Args:
            comment_repository (ICommentRepository): Comment repository
            user_service (IUserService): User service
        """
        self.comment_repository = comment_repository
        self.user_service = user_service

    async def get_by_recipe(self, recipe_id: int) -> List[Comment]:
        """Get all comments for a specific recipe.

        Args:
            recipe_id (int): The ID of the recipe

        Returns:
            List[Comment]: All comments for the recipe
            
        Raises:
            HTTPException: If recipe not found or there's an error fetching comments
        """
        try:
            comments = await self.comment_repository.get_by_recipe(recipe_id)
            if not comments:
                raise HTTPException(status_code=404, detail=f"No comments found for recipe {recipe_id}")
                
            result = []
            for comment in comments:
                if comment['rating_id'] is not None:
                    rating_data = await self.comment_repository.get_rating_by_id(comment['rating_id'])
                    if rating_data:
                        rating = Rating(
                            id=rating_data['id'],
                            value=rating_data['value'],
                            recipe_id=rating_data['recipe_id'],
                            author=rating_data['author'],
                            created_at=rating_data['created_at']
                        )
                        comment['rating'] = rating
                result.append(self._to_domain(comment))
            return result
        except Exception as e:
            if isinstance(e, HTTPException):
                raise
            raise HTTPException(status_code=500, detail=f"Error fetching comments: {str(e)}")

    async def get_by_user(self, user_id: UUID) -> List[Comment]:
        """Get all comments made by a specific user.

        Args:
            user_id (UUID): The ID of the user

        Returns:
            List[Comment]: All comments made by the user
            
        Raises:
            HTTPException: If user not found or there's an error fetching comments
        """
        try:
            comments = await self.comment_repository.get_by_user(user_id)
            if not comments:
                raise HTTPException(status_code=404, detail=f"No comments found for user {user_id}")
                
            result = []
            for comment in comments:
                if comment['rating_id'] is not None:
                    rating_data = await self.comment_repository.get_rating_by_id(comment['rating_id'])
                    if rating_data:
                        rating = Rating(
                            id=rating_data['id'],
                            value=rating_data['value'],
                            recipe_id=rating_data['recipe_id'],
                            author=rating_data['author'],
                            created_at=rating_data['created_at']
                        )
                        comment['rating'] = rating
                result.append(self._to_domain(comment))
            return result
        except Exception as e:
            if isinstance(e, HTTPException):
                raise
            raise HTTPException(status_code=500, detail=f"Error fetching user comments: {str(e)}")

    async def get_by_id(self, comment_id: int) -> Optional[Comment]:
        """Get a specific comment by its ID.

        Args:
            comment_id (int): The ID of the comment

        Returns:
            Optional[Comment]: The comment if found
            
        Raises:
            HTTPException: If comment not found or there's an error fetching it
        """
        try:
            comment = await self.comment_repository.get_by_id(comment_id)
            if not comment:
                raise HTTPException(status_code=404, detail=f"Comment {comment_id} not found")
                
            if comment['rating_id'] is not None:
                rating_data = await self.comment_repository.get_rating_by_id(comment['rating_id'])
                if rating_data:
                    rating = Rating(
                        id=rating_data['id'],
                        value=rating_data['value'],
                        recipe_id=rating_data['recipe_id'],
                        author=rating_data['author'],
                        created_at=rating_data['created_at']
                    )
                    comment['rating'] = rating
            return self._to_domain(comment)
        except Exception as e:
            if isinstance(e, HTTPException):
                raise
            raise HTTPException(status_code=500, detail=f"Error fetching comment: {str(e)}")

    async def add_comment(self, comment: CommentIn, author: UUID) -> Comment:
        """Add a new comment to a recipe.

        Args:
            comment (CommentIn): The comment data
            author (UUID): The ID of the user making the comment

        Returns:
            Comment: The newly created comment
            
        Raises:
            HTTPException: If comment creation fails or validation error occurs
        """
        try:
            # Create rating if value provided
            rating = None
            
            if comment.rating is not None and comment.rating.value is not None:
                if not 1 <= comment.rating.value <= 5:
                    raise HTTPException(
                        status_code=422,
                        detail="Rating value must be between 1 and 5"
                    )
                try:
                    rating = Rating(
                        value=comment.rating.value,
                        recipe_id=comment.recipe_id,
                        author=author,
                        created_at=datetime.now(timezone.utc)
                    )
                except ValidationError as e:
                    raise HTTPException(
                        status_code=422,
                        detail=f"Invalid rating value: {str(e)}"
                    )

            # Create comment domain object with optional rating
            comment_domain = Comment(
                content=comment.content,
                recipe_id=comment.recipe_id,
                author=author,
                created_at=datetime.now(timezone.utc)
            )
            
            # Add rating only if it was created
            if rating is not None:
                comment_domain.rating = rating

            # Add comment to repository
            created_comment = await self.comment_repository.add_comment(comment_domain, author)
            
            if not created_comment:
                raise HTTPException(status_code=400, detail="Failed to create comment")
                
            comment_with_rating = await self.get_by_id(created_comment['id'])
            if not comment_with_rating:
                raise HTTPException(status_code=500, detail="Failed to fetch created comment")
                
            return comment_with_rating
        except ValidationError as e:
            raise HTTPException(status_code=422, detail=str(e))
        except Exception as e:
            if isinstance(e, HTTPException):
                raise
            raise HTTPException(status_code=500, detail=f"Error creating comment: {str(e)}")

    async def update_comment(self, comment_id: int, comment: CommentIn, user_id: UUID) -> Comment:
        """Update an existing comment.

        Args:
            comment_id (int): The ID of the comment to update
            comment (CommentIn): The updated comment data
            user_id (UUID): The ID of the user making the update

        Returns:
            Comment: The updated comment
            
        Raises:
            HTTPException: If comment not found, user not authorized, or update fails
        """
        try:
            existing = await self.get_by_id(comment_id)
            if not existing:
                raise HTTPException(status_code=404, detail="Comment not found")

            if existing.author != user_id:
                is_admin = await self.user_service.is_admin(str(user_id))
                if not is_admin:
                    raise HTTPException(status_code=403, detail="Not authorized to update this comment")

            if comment.rating is not None and comment.rating.value is not None and not 1 <= comment.rating.value <= 5:
                raise HTTPException(status_code=400, detail="Rating must be between 1 and 5")

            comment_data = await self.comment_repository.update_comment(comment_id, comment)
            if not comment_data:
                raise HTTPException(status_code=500, detail="Failed to update comment")
                
            return self._to_domain(comment_data)
        except ValidationError as e:
            raise HTTPException(status_code=422, detail=str(e))
        except Exception as e:
            if isinstance(e, HTTPException):
                raise
            raise HTTPException(status_code=500, detail=f"Error updating comment: {str(e)}")

    async def delete_comment(self, comment_id: int, user_id: UUID) -> bool:
        """Delete a comment.

        Args:
            comment_id (int): The ID of the comment to delete
            user_id (UUID): The ID of the user requesting deletion

        Returns:
            bool: True if comment was deleted
            
        Raises:
            HTTPException: If comment not found, user not authorized, or delete fails
        """
        try:
            existing = await self.get_by_id(comment_id)
            if not existing:
                raise HTTPException(status_code=404, detail="Comment not found")

            if existing.author != user_id:
                is_admin = await self.user_service.is_admin(str(user_id))
                if not is_admin:
                    raise HTTPException(status_code=403, detail="Not authorized to delete this comment")

            deleted = await self.comment_repository.delete_comment(comment_id)
            if not deleted:
                raise HTTPException(status_code=500, detail="Failed to delete comment")
                
            return True
        except Exception as e:
            if isinstance(e, HTTPException):
                raise
            raise HTTPException(status_code=500, detail=f"Error deleting comment: {str(e)}")

    def _to_domain(self, record: Dict) -> Comment:
        """Convert database record to domain model.

        Args:
            record (Dict): Database record

        Returns:
            Comment: Domain model
        """
        rating = None
        if record.get("rating_id") is not None and record.get("value") is not None:
            rating = Rating(
                id=record["rating_id"],
                value=record["value"],
                recipe_id=record["rating_recipe_id"],
                author=record["rating_author"],
                created_at=record["rating_created_at"]
            )

        return Comment(
            id=record["id"],
            content=record["content"],
            recipe_id=record["recipe_id"],
            author=record["author"],
            created_at=record["created_at"],
            rating=rating
        )
