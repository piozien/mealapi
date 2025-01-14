"""Module containing report repository abstractions."""

from abc import ABC, abstractmethod
from typing import Any, Iterable

from uuid import UUID
from mealapi.core.domain.report import ReportIn, ReportStatus


class IReportRepository(ABC):
    """An abstract class representing protocol of report repository."""

    @abstractmethod
    async def get_all_reports(self) -> Iterable[Any]:
        """Get all reports.

        Returns:
            Iterable[Any]: All reports in the system
        """

    @abstractmethod
    async def get_by_status(self, status: ReportStatus) -> Iterable[Any]:
        """Get all reports with a specific status.

        Args:
            status (ReportStatus): The status to filter by

        Returns:
            Iterable[Any]: All reports with the given status
        """

    @abstractmethod
    async def get_by_comment(self, comment_id: int) -> Iterable[Any]:
        """Get all reports for a specific comment.

        Args:
            comment_id (int): The ID of the comment

        Returns:
            Iterable[Any]: All reports for the comment
        """

    @abstractmethod
    async def get_by_reporter(self, user_id: UUID) -> Iterable[Any]:
        """Get all reports made by a specific user.

        Args:
            user_id (UUID): The ID of the user who made the reports

        Returns:
            Iterable[Any]: All reports made by the user
        """

    @abstractmethod
    async def get_by_id(self, report_id: int) -> Any:
        """Get a specific report by its ID.

        Args:
            report_id (int): The ID of the report

        Returns:
            Any: The report if found
        """

    @abstractmethod
    async def add_report(self, report: ReportIn, reporter_id: UUID) -> Any:
        """Add a new report.

        Args:
            report (ReportIn): The report to add
            reporter_id (UUID): The ID of the user reporting the comment

        Returns:
            Any: The newly created report
        """

    @abstractmethod
    async def update_status(self, report_id: int, status: ReportStatus, resolved_by: UUID, resolution_note: str) -> Any:
        """Update the status of a report.

        Args:
            report_id (int): The ID of the report
            status (ReportStatus): The new status
            resolved_by (UUID7): The ID of the admin who resolved the report
            resolution_note (str): Note explaining the resolution

        Returns:
            Any: The updated report
        """

    @abstractmethod
    async def delete_report(self, report_id: int) -> bool:
        """Delete a report.

        Args:
            report_id (int): The ID of the report to delete

        Returns:
            bool: True if deleted successfully
        """
