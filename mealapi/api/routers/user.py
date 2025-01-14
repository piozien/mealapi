"""A module containing user endpoints."""

from dependency_injector.wiring import inject, Provide
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import jwt, JWTError
from uuid import UUID

from mealapi.infrastructure.utils.consts import SECRET_KEY, ALGORITHM
from mealapi.container import Container
from mealapi.core.domain.user import UserIn, UserRole
from mealapi.infrastructure.dto.tokendto import TokenDTO
from mealapi.infrastructure.dto.userdto import UserDTO
from mealapi.infrastructure.services.iuser import IUserService

bearer_scheme = HTTPBearer()
router = APIRouter(
    tags=["user"]
)


async def verify_admin_token(credentials: HTTPAuthorizationCredentials, user_service: IUserService) -> bool:
    """Verify if the token belongs to an admin user and the role matches database.

    Args:
        credentials (HTTPAuthorizationCredentials): The JWT credentials
        user_service (IUserService): The user service instance

    Returns:
        bool: True if token is valid and user is admin, False otherwise

    Raises:
        HTTPException: If token is invalid or user not found
    """
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        user_uuid = payload.get("sub")
        token_role = payload.get("role")
        
        if not user_uuid or not token_role:
            raise HTTPException(status_code=401, detail="Invalid token claims")
        
        user = await user_service.get_by_uuid(user_uuid)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
            
        # Verify that token role matches database role
        if token_role != user.role.value:
            raise HTTPException(status_code=401, detail="Token role mismatch")
            
        return user.role == UserRole.ADMIN
        
    except JWTError:
        raise HTTPException(status_code=401, detail="Could not validate credentials")


@router.post("/register", response_model=UserDTO, status_code=201)
@inject
async def register_user(
    user: UserIn,
    service: IUserService = Depends(Provide[Container.user_service]),
) -> dict:
    """An endpoint for registering a new user.

    Args:
        user (UserIn): The user data.
        service (IUserService): The injected service dependency.

    Returns:
        dict: The new user attributes.
    """
    if new_user := await service.register_user(user):
        return new_user
    raise HTTPException(status_code=400, detail="Registration failed")


@router.post("/token", response_model=TokenDTO, status_code=200)
@inject
async def authenticate_user(
    user: UserIn,
    service: IUserService = Depends(Provide[Container.user_service]),
) -> dict:
    """A router coroutine for authenticating users.

    Args:
        user (UserIn): The user input data.
        service (IUserService): The injected user service.

    Returns:
        dict: The token DTO details.
    """
    try:
        if token := await service.authenticate_user(user):
            return token
        raise HTTPException(status_code=401, detail="Invalid credentials")
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))


@router.put("/{user_id}/role", response_model=UserDTO, status_code=200)
@inject
async def update_user_role(
    user_id: UUID,
    role: UserRole,
    service: IUserService = Depends(Provide[Container.user_service]),
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> dict:
    """An endpoint for updating user role.

    Args:
        user_id (UUID4): The ID of the user to update.
        role (UserRole): The new role to assign.
        service (IUserService): The injected service dependency.
        credentials (HTTPAuthorizationCredentials): The credentials.

    Returns:
        dict: The updated user attributes.

    Raises:
        HTTPException: 403 if unauthorized or 404 if user not found.
    """
    if not await verify_admin_token(credentials, service):
        raise HTTPException(status_code=403, detail="Not authorized")

    if updated_user := await service.update_user_role(user_id, role):
        return updated_user
    raise HTTPException(status_code=404, detail="User not found")
