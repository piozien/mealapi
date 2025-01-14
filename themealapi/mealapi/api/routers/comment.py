"""A module containing comment endpoints."""

from typing import Iterable

from dependency_injector.wiring import inject, Provide
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import jwt
from uuid import UUID

from mealapi.infrastructure.utils.consts import SECRET_KEY, ALGORITHM
from mealapi.container import Container
from mealapi.core.domain.comment import CommentIn, CommentCreate
from mealapi.infrastructure.dto.commentdto import CommentDTO
from mealapi.infrastructure.services.icomment import ICommentService
from mealapi.infrastructure.services.iuser import IUserService

bearer_scheme = HTTPBearer()
router = APIRouter(
    tags=["comment"]
)


@router.post("/create", response_model=CommentDTO, status_code=201)
@inject
async def create_comment(
        comment: CommentCreate,
        service: ICommentService = Depends(Provide[Container.comment_service]),
        credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> CommentDTO:
    """Create a new comment.

    Args:
        comment: The comment data for creation
        service: The comment service (injected)
        credentials: User credentials

    Returns:
        The created comment

    Raises:
        HTTPException: If unauthorized or comment creation fails
    """
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        user_uuid = payload.get("sub")
        if not user_uuid:
            raise HTTPException(
                status_code=401,
                detail="Authentication failed: Invalid or missing user ID in token"
            )

        comment_data = CommentIn(
            content=comment.content,
            recipe_id=comment.recipe_id,
            rating=comment.rating
        )
        
        new_comment = await service.add_comment(comment_data, UUID(user_uuid))
        if not new_comment:
            raise HTTPException(
                status_code=500,
                detail="Server error: Failed to create comment"
            )
        return new_comment

    except jwt.JWTError:
        raise HTTPException(
            status_code=401,
            detail="Authentication failed: Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Validation error: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Server error: {str(e)}"
        )


@router.get("/recipe/{recipe_id}", response_model=list[CommentDTO])
@inject
async def get_recipe_comments(
    recipe_id: int,
    service: ICommentService = Depends(Provide[Container.comment_service]),
) -> Iterable[CommentDTO]:
    """Get all comments for a recipe.

    Args:
        recipe_id: The ID of the recipe
        service: The comment service (injected)

    Returns:
        All comments for the recipe

    Raises:
        HTTPException: If recipe not found
    """
    try:
        comments = await service.get_by_recipe(recipe_id)
        if not comments:
            raise HTTPException(
                status_code=404,
                detail=f"Not found: No comments found for recipe {recipe_id}"
            )
        return comments

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Validation error: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Server error: {str(e)}"
        )


@router.get("/user/{user_id}", response_model=list[CommentDTO])
@inject
async def get_user_comments(
    user_id: UUID,
    service: ICommentService = Depends(Provide[Container.comment_service]),
    user_service: IUserService = Depends(Provide[Container.user_service]),
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> Iterable[CommentDTO]:
    """Get all comments by a user.

    Args:
        user_id: The ID of the user
        service: The comment service (injected)
        user_service: The user service (injected)
        credentials: User credentials

    Returns:
        All comments by the user

    Raises:
        HTTPException: If unauthorized or user not found
    """
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        requester_uuid = payload.get("sub")
        if not requester_uuid:
            raise HTTPException(
                status_code=401,
                detail="Authentication failed: Invalid or missing user ID in token"
            )

        # Only admins or the user themselves can view their comments
        if UUID(requester_uuid) != user_id and not await user_service.is_admin(UUID(requester_uuid)):
            raise HTTPException(
                status_code=403,
                detail="Access denied: Can only view your own comments or must be an administrator"
            )

        comments = await service.get_by_user(user_id)
        if not comments:
            raise HTTPException(
                status_code=404,
                detail=f"Not found: No comments found for user {user_id}"
            )
        return comments

    except jwt.JWTError:
        raise HTTPException(
            status_code=401,
            detail="Authentication failed: Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Validation error: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Server error: {str(e)}"
        )


@router.put("/comments/{comment_id}", response_model=CommentDTO)
@inject
async def update_comment(
    comment_id: int,
    updated_comment: CommentIn,
    service: ICommentService = Depends(Provide[Container.comment_service]),
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> CommentDTO:
    """Update a comment.

    Args:
        comment_id: The ID of the comment
        updated_comment: The updated comment data
        service: The comment service (injected)
        credentials: User credentials

    Returns:
        The updated comment

    Raises:
        HTTPException: If unauthorized or comment not found
    """
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        user_uuid = payload.get("sub")
        if not user_uuid:
            raise HTTPException(
                status_code=401,
                detail="Authentication failed: Invalid or missing user ID in token"
            )

        comment = await service.update_comment(comment_id, updated_comment, UUID(user_uuid))
        if not comment:
            raise HTTPException(
                status_code=404,
                detail=f"Not found: Comment with ID {comment_id} does not exist"
            )
        return comment

    except jwt.JWTError:
        raise HTTPException(
            status_code=401,
            detail="Authentication failed: Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Validation error: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Server error: {str(e)}"
        )


@router.delete("/comments/{comment_id}", status_code=204)
@inject
async def delete_comment(
    comment_id: int,
    service: ICommentService = Depends(Provide[Container.comment_service]),
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> None:
    """Delete a comment.

    Args:
        comment_id: The ID of the comment
        service: The comment service (injected)
        credentials: User credentials

    Raises:
        HTTPException: If unauthorized or comment not found
    """
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        user_uuid = payload.get("sub")
        if not user_uuid:
            raise HTTPException(
                status_code=401,
                detail="Authentication failed: Invalid or missing user ID in token"
            )

        if not await service.delete_comment(comment_id, UUID(user_uuid)):
            raise HTTPException(
                status_code=404,
                detail=f"Not found: Comment with ID {comment_id} does not exist"
            )

    except jwt.JWTError:
        raise HTTPException(
            status_code=401,
            detail="Authentication failed: Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Validation error: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Server error: {str(e)}"
        )
