"""Module containing report related domain models.

This module defines the data models for handling content reports in the application.
Reports allow users to flag inappropriate content, spam, or other issues with recipes and comments.
"""

from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, ConfigDict
from uuid import UUID


class ReportStatus(str, Enum):
    """Status of a content report.
    
    Values:
        PENDING: Report is awaiting review by administrators
        RESOLVED: Report has been reviewed and action was taken
        REJECTED: Report was reviewed but no action was necessary
    """
    PENDING = "pending"
    RESOLVED = "resolved"
    REJECTED = "rejected"


class ReportReason(str, Enum):
    """Common reasons for reporting content.
    
    Values:
        INAPPROPRIATE: Content violates community guidelines
        SPAM: Content is spam or advertising
        HARASSMENT: Content contains harassment or personal attacks
        OTHER: Other reasons not covered by specific categories
    """
    INAPPROPRIATE = "inappropriate_content"
    SPAM = "spam"
    HARASSMENT = "harassment"
    OTHER = "other"


class ReportIn(BaseModel):
    """Model for creating a new content report.
    
    Attributes:
        recipe_id (int): ID of the recipe being reported (if reporting a recipe)
        comment_id (int): ID of the comment being reported (if reporting a comment)
        reason (ReportReason): The reason for reporting the content
        description (str): Detailed explanation of the issue
    """
    recipe_id: int
    comment_id: int
    reason: ReportReason
    description: str


class Report(ReportIn):
    """Model representing a complete report in the database.
    
    Extends ReportIn to include additional fields for report tracking and resolution.
    
    Attributes:
        id (int): Unique identifier of the report
        created_at (datetime): Timestamp when the report was created
        status (ReportStatus): Current status of the report
        resolved_by (Optional[UUID]): ID of the administrator who handled the report
        resolution_note (Optional[str]): Administrator's note about how the report was handled
        resolved_at (Optional[datetime]): Timestamp when the report was resolved
    """
    id: int
    created_at: datetime
    status: ReportStatus = ReportStatus.PENDING
    resolved_by: Optional[UUID] = None
    resolution_note: Optional[str] = None
    resolved_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True, extra="ignore")
