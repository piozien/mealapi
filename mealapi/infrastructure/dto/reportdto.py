"""A module containing DTO models for output reports."""

from datetime import datetime
from typing import Optional
from asyncpg import Record
from pydantic import BaseModel, ConfigDict
from uuid import UUID

from mealapi.core.domain.report import ReportStatus, ReportReason


class ReportDTO(BaseModel):
    """A model representing DTO for report data."""
    id: int
    reporter_id: UUID
    recipe_id: Optional[int] = None
    comment_id: Optional[int] = None
    reason: ReportReason
    description: Optional[str] = None
    created_at: datetime
    status: ReportStatus = ReportStatus.PENDING
    resolved_by: Optional[UUID] = None
    resolution_note: Optional[str] = None
    resolved_at: Optional[datetime] = None

    model_config = ConfigDict(
        from_attributes=True,
        extra="ignore",
        arbitrary_types_allowed=True,
    )

    @classmethod
    def from_record(cls, record: Record) -> "ReportDTO":
        """Create a ReportDTO from a database record.

        Args:
            record (Record): The database record

        Returns:
            ReportDTO: The created DTO
        """
        record_dict = dict(record)
        return cls(
            id=record_dict.get("id"),  # type: ignore
            reporter_id=record_dict.get("reporter_id"),  # type: ignore
            recipe_id=record_dict.get("recipe_id"),  # type: ignore
            comment_id=record_dict.get("comment_id"),  # type: ignore
            reason=ReportReason(record_dict.get("reason")),  # type: ignore
            description=record_dict.get("description"),
            created_at=record_dict.get("created_at"),  # type: ignore
            status=ReportStatus(record_dict.get("status")),  # type: ignore
            resolved_by=record_dict.get("resolved_by"),
            resolution_note=record_dict.get("resolution_note"),
            resolved_at=record_dict.get("resolved_at")
        )
