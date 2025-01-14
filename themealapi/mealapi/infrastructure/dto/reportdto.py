"""Module containing report data transfer objects.

This module defines the DTO (Data Transfer Object) models for content reports,
which are used to transfer report data between different layers of the application
and to format the response data sent to clients, including associated comment data.
"""

from datetime import datetime
from typing import Optional
from asyncpg import Record
from pydantic import BaseModel, ConfigDict, field_validator
from uuid import UUID

from mealapi.core.domain.report import ReportStatus, ReportReason
from mealapi.infrastructure.dto.commentdto import CommentDTO


class ReportDTO(BaseModel):
    """Data Transfer Object for content reports.
    
    This class represents the report data that is sent to clients in API responses.
    It includes all report information along with the associated reported content.
    
    Attributes:
        id (int): Unique identifier of the report
        reporter_id (UUID): ID of the user who created the report
        recipe_id (int): ID of the recipe being reported
        comment (CommentDTO): The reported comment, if reporting a comment
        reason (ReportReason): Reason for the report (e.g., SPAM, INAPPROPRIATE)
        description (Optional[str]): Additional details about the report
        created_at (datetime): Timestamp when the report was created
        status (ReportStatus): Current status of the report (default: PENDING)
        resolved_by (Optional[UUID]): ID of the admin who handled the report
        resolution_note (Optional[str]): Admin's note about resolution
        resolved_at (Optional[datetime]): Timestamp when the report was resolved
    """
    id: int
    reporter_id: UUID
    recipe_id: int
    comment: CommentDTO
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

    @field_validator('created_at', 'resolved_at')
    @classmethod
    def ensure_timezone(cls, v: Optional[datetime]) -> Optional[datetime]:
        """Ensure datetime fields are timezone-aware in UTC.
        
        Args:
            v (Optional[datetime]): The datetime value to validate

        Returns:
            Optional[datetime]: The validated datetime value
        """
        if v is None:
            return None
        return v

    @classmethod
    def from_record(cls, record: Record) -> "ReportDTO":
        """Create a ReportDTO from a database record.

        This method handles the conversion of database records into ReportDTO instances,
        including the processing of nested comment data.

        Args:
            record (Record): Database record containing report data and related entities

        Returns:
            ReportDTO: A new ReportDTO instance containing the report data and its relations

        Example:
            >>> record = {
            ...     "id": 1,
            ...     "reporter_id": UUID("550e8400-e29b-41d4-a716-446655440000"),
            ...     "recipe_id": 123,
            ...     "comment": {"id": 1, "content": "Reported comment"},
            ...     "reason": "SPAM",
            ...     "created_at": datetime.now()
            ... }
            >>> report_dto = ReportDTO.from_record(record)
        """
        record_dict = dict(record)
        
        if 'comment' in record_dict and record_dict['comment']:
            record_dict['comment'] = CommentDTO.from_record(record_dict['comment'])
            
        return cls(**record_dict)