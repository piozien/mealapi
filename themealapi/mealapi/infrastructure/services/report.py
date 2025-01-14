"""A module containing report service implementation."""

from typing import Iterable, Optional, Any
from uuid import UUID

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
        """
        return await self._repository.get_all_reports()
    
    async def get_by_status(self, status: ReportStatus) -> Iterable[Report]:
        """Get all reports with a specific status.

        Args:
            status (ReportStatus): The status to filter by

        Returns:
            Iterable[Report]: All reports with the given status
        """
        return await self._repository.get_by_status(status)
        
    async def get_by_comment(self, comment_id: int) -> Iterable[Report]:
        """Get all reports for a specific comment.

        Args:
            comment_id (int): The ID of the comment

        Returns:
            Iterable[Report]: All reports for the comment
        """
        return await self._repository.get_by_comment(comment_id)
        
    async def get_by_reporter(self, user_id: UUID) -> Iterable[Report]:
        """Get all reports made by a specific user.

        Args:
            user_id (UUID): The ID of the user who made the reports

        Returns:
            Iterable[Report]: All reports made by the user
        """
        return await self._repository.get_by_reporter(user_id)
    
    async def add_report(self, report: ReportIn, reporter_id: UUID) -> Any | None:
        """Add a new report.

        Args:
            report (ReportIn): The report to add
            reporter_id (UUID): ID of the user creating the report

        Returns:
            Any | None: The newly created report
        """
        return await self._repository.add_report(report, reporter_id)
        
    async def update_status(
        self,
        report_id: int,
        status: ReportStatus,
        resolved_by: UUID | None = None,
        resolution_note: str | None = None,
    ) -> Report | None:
        """Update the status of a report.

        Args:
            report_id (int): The ID of the report to update
            status (ReportStatus): The new status
            resolved_by (UUID | None): ID of the admin who resolved the report
            resolution_note (str | None): Note explaining the resolution

        Returns:
            Report | None: The updated report
        """
        return await self._repository.update_status(report_id, status, resolved_by, resolution_note)
        
    async def delete_report(self, report_id: int) -> bool:
        """Delete a report.

        Args:
            report_id (int): The ID of the report to delete

        Returns:
            bool: True if deleted successfully
        """
        return await self._repository.delete_report(report_id)