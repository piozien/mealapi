"""Module containing report related domain models"""

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict
from uuid import UUID


class ReportStatus(str, Enum):
    """Status of a report"""
    PENDING = "pending"
    RESOLVED = "resolved"
    REJECTED = "rejected"


class ReportReason(str, Enum):
    """Common reasons for reporting"""
    INAPPROPRIATE = "inappropriate_content"
    SPAM = "spam"
    HARASSMENT = "harassment"
    OTHER = "other"


class ReportIn(BaseModel):
    """Class representing report input data."""

    recipe_id: Optional[int] = None
    comment_id: Optional[int] = None
    reason: ReportReason
    description: str

    model_config = ConfigDict(from_attributes=True, extra="ignore")


class Report(ReportIn):
    """Model representing a report in the database"""
    id: int
    reporter_id: UUID
    created_at: datetime
    status: ReportStatus = ReportStatus.PENDING
    resolved_by: Optional[UUID] = None
    resolution_note: Optional[str] = None
    resolved_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True, extra="ignore")
