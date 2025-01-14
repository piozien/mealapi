"""A module containing comment endpoints."""

from typing import Iterable
from datetime import datetime


from dependency_injector.wiring import inject, Provide
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import jwt
from uuid import UUID

from mealapi.infrastructure.utils.consts import SECRET_KEY, ALGORITHM
from mealapi.container import Container
from mealapi.core.domain.comment import CommentIn, Comment, CommentCreate
from mealapi.infrastructure.dto.commentdto import CommentDTO
from mealapi.infrastructure.services.icomment import ICommentService
from mealapi.infrastructure.services.iuser import IUserService
from mealapi.core.domain.user import UserRole

bearer_scheme = HTTPBearer()
router = APIRouter(
    tags=["comment"],
    responses={
        401: {"description": "Unauthorized"},
        403: {"description": "Forbidden - insufficient permissions"},
        404: {"description": "Not Found"},
    }
)


async def is_admin(user_uuid: str, user_service: IUserService) -> bool:
    """Check if the user has admin role.

    Args:
        user_uuid (str): The UUID of the user to check
        user_service (IUserService): The user service instance

    Returns:
        bool: True if user is admin, False otherwise
    """
    user = await user_service.get_by_uuid(user_uuid)
    return user is not None and user.role == UserRole.ADMIN


@router.post("/create", response_model=CommentDTO, status_code=201)
@inject
async def create_comment(
        comment: CommentCreate,
        service: ICommentService = Depends(Provide[Container.comment_service]),
        credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> CommentDTO:
    """An endpoint for adding new comment.

    Args:
        comment (CommentCreate): The comment data for creation.
        service (ICommentService): The injected service dependency.
        credentials (HTTPAuthorizationCredentials): The credentials.

    Returns:
        dict: The created comment attributes.

    Raises:
        HTTPException: If token is invalid or comment creation fails.
    """
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        user_uuid = payload.get("sub")
        if not user_uuid:
            raise HTTPException(
                status_code=401,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        comment_domain = Comment(
            recipe_id=comment.recipe_id,
            content=comment.content,
            rating=comment.rating,
            author=UUID(user_uuid),
            created_at=datetime.utcnow()
        )
        created_comment = await service.add_comment(comment_domain)
        if not created_comment:
            raise HTTPException(
                status_code=400,
                detail="Failed to create recipe"
            )
        return created_comment

    except jwt.JWTError:
        raise HTTPException(
            status_code=401,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.get("/recipe/{recipe_id}", response_model=list[CommentDTO])
@inject
async def get_recipe_comments(
    recipe_id: int,
        service: ICommentService = Depends(Provide[Container.comment_service]),
) -> Iterable[CommentDTO]:
    """An endpoint for getting all comments for a recipe.

    Args:
        recipe_id (int): The ID of the recipe.
        service (ICommentService): The injected service dependency.

    Returns:
        Iterable[CommentDTO]: All comments for the recipe.
    """
    return await service.get_by_recipe(recipe_id)


@router.get("/user/{user_id}", response_model=list[CommentDTO])
@inject
async def get_user_comments(
    user_id: UUID,
        service: ICommentService = Depends(Provide[Container.comment_service]),
        user_service: IUserService = Depends(Provide[Container.user_service]),
        credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> Iterable[CommentDTO]:
    """An endpoint for getting all comments by a user.

    Args:
        user_id (UUID7): The ID of the user.
        service (ICommentService): The injected service dependency.
        user_service (IUserService): The injected user service dependency.
        credentials (HTTPAuthorizationCredentials): The credentials.

    Returns:
        Iterable[CommentDTO]: All comments by the user.

    Raises:
        HTTPException: If token is invalid or user is not authorized.
    """
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        current_user = UUID(payload.get("sub"))

        if current_user != user_id and not await is_admin(str(current_user), user_service):
            raise HTTPException(
                status_code=403,
                detail="Not enough permissions to view other user's comments"
            )

        return await service.get_by_user(user_id)
    except jwt.JWTError:
        raise HTTPException(
            status_code=401,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.put("/{comment_id}", response_model=CommentDTO)
@inject
async def update_comment(
        comment_id: int,
        updated_comment: CommentIn,
    service: ICommentService = Depends(Provide[Container.comment_service]),
        user_service: IUserService = Depends(Provide[Container.user_service]),
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> dict:
    """An endpoint for updating a comment.

    Args:
        comment_id (int): The ID of the comment.
        updated_comment (CommentIn): The updated comment data.
        service (ICommentService): The injected service dependency.
        user_service (IUserService): The injected user service dependency.
        credentials (HTTPAuthorizationCredentials): The credentials.

    Returns:
        dict: The updated comment attributes.

    Raises:
        HTTPException: If token is invalid or user is not authorized.
    """
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        current_user = UUID(payload.get("sub"))

        comment = await service.get_by_id(comment_id)
        if not comment:
            raise HTTPException(status_code=404, detail="Comment not found")

        if comment.author != current_user and not await is_admin(str(current_user), user_service):
            raise HTTPException(
                status_code=403,
                detail="Not enough permissions to update this comment"
            )

        return await service.update_comment(comment_id, updated_comment)
    except jwt.JWTError:
        raise HTTPException(
            status_code=401,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.delete("/comments/{comment_id}", response_model=bool)
@inject
async def delete_comment(
    comment_id: int,
    user_uuid: str,
    service: ICommentService = Depends(Provide[Container.comment_service]),
    user_service: IUserService = Depends(Provide[Container.user_service]),
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> bool:
    """An endpoint for deleting a comment.

    Args:
        comment_id (int): The ID of the comment.
        user_uuid (str): The UUID of the user.
        service (ICommentService): The injected service dependency.
        user_service (IUserService): The injected user service dependency.
        credentials (HTTPAuthorizationCredentials): The credentials.

    Returns:
        bool: True if comment was deleted successfully.

    Raises:
        HTTPException: 404 if comment not found or 403 if unauthorized.
    """
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        current_user = UUID(payload.get("sub"))

        if not await is_admin(str(current_user), user_service):
            comment = await service.get_by_id(comment_id)
            if not comment or str(comment.author) != user_uuid:
                raise HTTPException(
                    status_code=403,
                    detail="Not authorized to delete this comment"
                )

        await service.delete_comment(comment_id, UUID(user_uuid))
        return True
    except jwt.JWTError:
        raise HTTPException(
            status_code=401,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
