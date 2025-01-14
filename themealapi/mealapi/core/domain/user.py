"""Module containing user-related domain models.

This module defines the core data models for user management in the application.
It includes user roles and authentication-related models.
"""

from enum import Enum
from pydantic import BaseModel, ConfigDict
from uuid import UUID


class UserRole(str, Enum):
    """User role types for access control.
    
    Values:
        ADMIN: Administrator with full access to all features
        USER: Regular user with standard permissions
    """
    ADMIN = "ADMIN"
    USER = "USER"


class UserIn(BaseModel):
    """Model for user registration and authentication.
    
    Attributes:
        email (str): User's email address (used as username)
        password (str): User's password (should be hashed before storage)
        role (UserRole): User's role in the system (defaults to USER)
    """
    email: str
    password: str
    role: UserRole = UserRole.USER


class User(UserIn):
    """Model representing a complete user in the database.
    
    Extends UserIn to include additional fields for user identification.
    
    Attributes:
        id (UUID): Unique identifier of the user
    """
    id: UUID

    model_config = ConfigDict(from_attributes=True, extra="ignore")
