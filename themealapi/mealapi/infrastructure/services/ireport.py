"""Module containing report service abstractions."""
from abc import ABC, abstractmethod
from typing import Iterable, Optional

from uuid import UUID

from mealapi.core.domain.report import Report, ReportIn, ReportStatus
from mealapi.infrastructure.dto.reportdto import ReportDTO


class IReportService(ABC):
    """An abstract class representing protocol of report service."""

    @abstractmethod
    async def get_all_reports(self) -> Iterable[ReportDTO]:
        """Get all reports.

        Returns:
            Iterable[ReportDTO]: All reports in the system
        """

    @abstractmethod
    async def get_by_status(self, status: ReportStatus) -> Iterable[ReportDTO]:
        """Get all reports with a specific status.

        Args:
            status (ReportStatus): The status to filter by

        Returns:
            Iterable[ReportDTO]: All reports with the given status
        """

    @abstractmethod
    async def get_by_comment(self, comment_id: int) -> Iterable[ReportDTO]:
        """Get all reports for a specific comment.

        Args:
            comment_id (int): The ID of the comment

        Returns:
            Iterable[ReportDTO]: All reports for the comment
        """

    @abstractmethod
    async def get_by_reporter(self, user_id: UUID) -> Iterable[ReportDTO]:
        """Get all reports made by a specific user.

        Args:
            user_id (UUID): The ID of the user who made the reports

        Returns:
            Iterable[ReportDTO]: All reports made by the user
        """

    @abstractmethod
    async def add_report(self, report: ReportIn) -> ReportDTO | None:
        """Add a new report.

        Args:
            report (ReportIn): The report to add

        Returns:
            ReportDTO | None: The newly created report
        """

    @abstractmethod
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

    @abstractmethod
    async def delete_report(self, report_id: int) -> bool:
        """Delete a report.

        Args:
            report_id (int): The ID of the report to delete

        Returns:
            bool: True if deleted successfully
        """