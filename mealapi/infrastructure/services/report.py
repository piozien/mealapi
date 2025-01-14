"""A module containing report service implementation."""

from typing import Iterable, Any
from uuid import UUID
from fastapi import HTTPException

from mealapi.core.domain.report import Report, ReportIn, ReportStatus
from mealapi.core.repositories.ireport import IReportRepository
from mealapi.infrastructure.services.ireport import IReportService


class ReportService(IReportService):
    """A class representing report service."""

    def __init__(self, repository: IReportRepository) -> None:
        """The initializer of the report service.

        Args:
            repository (IReportRepository): The report repository.
        """
        self._repository = repository

    async def get_all_reports(self) -> Iterable[Report]:
        """Get all reports.

        Returns:
            Iterable[Report]: All reports in the system
            
        Raises:
            HTTPException: If there's an error fetching reports
        """
        try:
            reports = await self._repository.get_all_reports()
            if not reports:
                raise HTTPException(status_code=404, detail="No reports found")
            return reports
        except Exception as e:
            if isinstance(e, HTTPException):
                raise
            raise HTTPException(status_code=500, detail=f"Error fetching reports: {str(e)}")
    
    async def get_by_status(self, status: ReportStatus) -> Iterable[Report]:
        """Get all reports with a specific status.

        Args:
            status (ReportStatus): The status to filter by

        Returns:
            Iterable[Report]: All reports with the given status
            
        Raises:
            HTTPException: If no reports found with status or there's an error
        """
        try:
            reports = await self._repository.get_by_status(status)
            if not reports:
                raise HTTPException(status_code=404, detail=f"No reports found with status {status}")
            return reports
        except Exception as e:
            if isinstance(e, HTTPException):
                raise
            raise HTTPException(status_code=500, detail=f"Error fetching reports by status: {str(e)}")
        
    async def get_by_comment(self, comment_id: int) -> Iterable[Report]:
        """Get all reports for a specific comment.

        Args:
            comment_id (int): The ID of the comment

        Returns:
            Iterable[Report]: All reports for the comment
            
        Raises:
            HTTPException: If comment not found or there's an error fetching reports
        """
        try:
            reports = await self._repository.get_by_comment(comment_id)
            if not reports:
                raise HTTPException(status_code=404, detail=f"No reports found for comment {comment_id}")
            return reports
        except Exception as e:
            if isinstance(e, HTTPException):
                raise
            raise HTTPException(status_code=500, detail=f"Error fetching reports for comment: {str(e)}")
        
    async def get_by_reporter(self, user_id: UUID) -> Iterable[Report]:
        """Get all reports made by a specific user.

        Args:
            user_id (UUID): The ID of the user who made the reports

        Returns:
            Iterable[Report]: All reports made by the user
            
        Raises:
            HTTPException: If no reports found for user or there's an error
        """
        try:
            reports = await self._repository.get_by_reporter(user_id)
            if not reports:
                raise HTTPException(status_code=404, detail=f"No reports found for user {user_id}")
            return reports
        except Exception as e:
            if isinstance(e, HTTPException):
                raise
            raise HTTPException(status_code=500, detail=f"Error fetching user reports: {str(e)}")

    async def get_by_id(self, report_id: int) -> Report | None:
        """Get a report by its ID.

        Args:
            report_id (int): The ID of the report

        Returns:
            Report | None: The report if found
            
        Raises:
            HTTPException: If report not found or there's an error fetching it
        """
        try:
            report = await self._repository.get_by_id(report_id)
            if not report:
                raise HTTPException(status_code=404, detail=f"Report {report_id} not found")
            return report
        except Exception as e:
            if isinstance(e, HTTPException):
                raise
            raise HTTPException(status_code=500, detail=f"Error fetching report: {str(e)}")

    async def add_report(self, report: ReportIn, reporter_id: UUID) -> Report:
        """Add a new report.

        Args:
            report (ReportIn): The report to add
            reporter_id (UUID): ID of the user creating the report

        Returns:
            Report: The newly created report
            
        Raises:
            HTTPException: If report creation fails or validation error occurs
        """
        try:
            report_data = await self._repository.add_report(report, reporter_id)
            if not report_data:
                raise HTTPException(status_code=500, detail="Failed to create report")
            return report_data
        except Exception as e:
            if isinstance(e, HTTPException):
                raise
            raise HTTPException(status_code=500, detail=f"Error creating report: {str(e)}")
        
    async def update_report_status(
        self,
        report_id: int,
        status: ReportStatus,
        resolved_by: UUID | None = None,
        resolution_note: str | None = None,
    ) -> Report:
        """Update the status of a report.

        Args:
            report_id (int): The ID of the report to update
            status (ReportStatus): The new status
            resolved_by (UUID | None): ID of the admin who resolved the report
            resolution_note (str | None): Note explaining the resolution

        Returns:
            Report: The updated report
            
        Raises:
            HTTPException: If report not found, invalid status transition, or update fails
        """
        try:
            existing = await self.get_by_id(report_id)
            if not existing:
                raise HTTPException(status_code=404, detail="Report not found")
                
            # Validate status transition
            if existing.status == ReportStatus.RESOLVED and status != ReportStatus.RESOLVED:
                raise HTTPException(status_code=400, detail="Cannot change status of resolved report")
                
            if status == ReportStatus.RESOLVED and not resolved_by:
                raise HTTPException(status_code=400, detail="Resolver ID required when marking as resolved")
                
            report_data = await self._repository.update_status(
                report_id, 
                status, 
                resolved_by, 
                resolution_note
            )
            if not report_data:
                raise HTTPException(status_code=500, detail="Failed to update report status")
                
            return report_data
        except Exception as e:
            if isinstance(e, HTTPException):
                raise
            raise HTTPException(status_code=500, detail=f"Error updating report status: {str(e)}")
        
    async def delete_report(self, report_id: int) -> bool:
        """Delete a report.

        Args:
            report_id (int): The ID of the report to delete

        Returns:
            bool: True if deleted successfully
            
        Raises:
            HTTPException: If report not found or deletion fails
        """
        try:
            report = await self.get_by_id(report_id)
            if not report:
                raise HTTPException(status_code=404, detail=f"Report {report_id} not found")
            return await self._repository.delete_report(report_id)
        except Exception as e:
            if isinstance(e, HTTPException):
                raise
            raise HTTPException(status_code=500, detail=f"Error deleting report: {str(e)}")
