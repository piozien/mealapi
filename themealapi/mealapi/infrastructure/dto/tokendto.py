"""Module containing authentication token data transfer objects.

This module defines the DTO (Data Transfer Object) models for authentication tokens,
which are used to transfer token data in authentication responses.
"""


from datetime import datetime
from pydantic import BaseModel, ConfigDict


class TokenDTO(BaseModel):
    """Data Transfer Object for authentication tokens.
    
    This class represents the token data that is sent to clients after successful authentication.
    
    Attributes:
        token_type (str): Type of the token (e.g., "bearer")
        user_token (str): The actual JWT token string
        expires (datetime): Timestamp when the token expires
    """
    token_type: str
    user_token: str
    expires: datetime

    model_config = ConfigDict(
        from_attributes=True,
        extra="ignore",
    )
