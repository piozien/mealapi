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
    tags=["user"],
    responses={
        401: {"description": "Unauthorized"},
        403: {"description": "Forbidden - insufficient permissions"},
        404: {"description": "Not Found"},
    }
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
) -> UserDTO:
    """Register a new user.

    Args:
        user (UserIn): User registration data

    Example request body:
        {
            "email": "user@example.com",
            "password": "securepassword123"
        }

    Returns:
        UserDTO: Created user data (without password)

    Example response:
        {
            "id": "123e4567-e89b-12d3-a456-426614174000",
            "email": "user@example.com",
            "role": "USER"
        }

    Raises:
        HTTPException: 400 if email already exists or invalid data
    """
    try:
        new_user = await service.register_user(user)
        if new_user is None:
            raise HTTPException(
                status_code=400,
                detail="Could not create user. Email might already be taken."
            )
        return new_user
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/token", response_model=TokenDTO, status_code=200)
@inject
async def authenticate_user(
    user: UserIn,
    service: IUserService = Depends(Provide[Container.user_service]),
) -> dict:
    """Login user and get access token.

    Args:
        user (UserIn): User login credentials

    Example request body:
        {
            "email": "user@example.com",
            "password": "securepassword123"
        }

    Returns:
        dict: JWT access token and token type

    Example response:
        {
            "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
            "token_type": "bearer"
        }

    Raises:
        HTTPException: 401 if invalid credentials
    """
    try:
        if token := await service.authenticate_user(user):
            return token
        raise HTTPException(status_code=401, detail="Invalid credentials")
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))


@router.get("/me", response_model=UserDTO)
@inject
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    service: IUserService = Depends(Provide[Container.user_service])
) -> UserDTO:
    """Get current user data.

    Returns:
        UserDTO: Current user data

    Example response:
        {
            "id": "123e4567-e89b-12d3-a456-426614174000",
            "email": "user@example.com",
            "role": "USER"
        }

    Raises:
        HTTPException: 401 if invalid or expired token
    """
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=401,
                detail="Could not validate credentials",
            )

        user = await service.get_by_uuid(UUID(user_id))
        if user is None:
            raise HTTPException(
                status_code=401,
                detail="User not found",
            )

        return user

    except jwt.JWTError:
        raise HTTPException(
            status_code=401,
            detail="Could not validate credentials",
        )


@router.put("/{user_id}/role", response_model=UserDTO, status_code=200)
@inject
async def update_user_role(
    user_id: UUID,
    role: UserRole,
    service: IUserService = Depends(Provide[Container.user_service]),
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> UserDTO:
    """Update user role.

    Args:
        user_id (UUID4): The ID of the user to update.
        role (UserRole): The new role to assign.

    Example request body:
        {
            "role": "ADMIN"
        }

    Returns:
        UserDTO: Updated user data

    Example response:
        {
            "id": "123e4567-e89b-12d3-a456-426614174000",
            "email": "user@example.com",
            "role": "ADMIN"
        }

    Raises:
        HTTPException: 403 if unauthorized or 404 if user not found.
    """
    if not await verify_admin_token(credentials, service):
        raise HTTPException(status_code=403, detail="Not authorized")

    if updated_user := await service.update_user_role(user_id, role):
        return updated_user
    raise HTTPException(status_code=404, detail="User not found")
