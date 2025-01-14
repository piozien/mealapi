"""Module containing report repository abstractions.

This module defines the interface for report repositories, specifying
the contract that any report repository implementation must fulfill.
The interface provides methods for managing content reports in the
data storage, including creation, retrieval, and resolution of reports.
"""

from abc import ABC, abstractmethod
from typing import Any, Iterable
from uuid import UUID
from mealapi.core.domain.report import ReportIn, ReportStatus


class IReportRepository(ABC):
    """Abstract base class defining the report repository interface.
    
    This interface defines all operations that must be supported by
    any concrete report repository implementation. It provides methods
    for managing content reports, including creation, retrieval by
    various criteria, and report resolution.
    """

    @abstractmethod
    async def get_all_reports(self) -> Iterable[Any]:
        """Retrieve all reports from the system.

        Returns:
            Iterable[Any]: Collection of all reports

        Note:
            Reports should be ordered by creation date, with the
            most recent reports first.
        """

    @abstractmethod
    async def get_by_status(self, status: ReportStatus) -> Iterable[Any]:
        """Retrieve all reports with a specific status.

        Args:
            status (ReportStatus): Status to filter by (e.g., PENDING, RESOLVED)

        Returns:
            Iterable[Any]: Collection of reports with the given status

        Note:
            Results should be ordered by creation date, with the
            oldest pending reports first.
        """

    @abstractmethod
    async def get_by_comment(self, comment_id: int) -> Iterable[Any]:
        """Retrieve all reports for a specific comment.

        Args:
            comment_id (int): ID of the reported comment

        Returns:
            Iterable[Any]: Collection of reports for the comment

        Note:
            Multiple reports may exist for the same comment from
            different users.
        """

    @abstractmethod
    async def get_by_reporter(self, user_id: UUID) -> Iterable[Any]:
        """Retrieve all reports made by a specific user.

        Args:
            user_id (UUID): ID of the user who made the reports

        Returns:
            Iterable[Any]: Collection of reports made by the user

        Note:
            Results should be ordered by creation date, with the
            most recent reports first.
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
    async def add_report(self, report: ReportIn) -> Any:
        """Create a new content report.

        Args:
            report (ReportIn): Report data to create

        Returns:
            Any: The created report with generated ID and metadata

        Note:
            The method should validate that the same user hasn't
            already reported the same content.
        """

    @abstractmethod
    async def update_status(self, report_id: int, status: ReportStatus, resolved_by: UUID, resolution_note: str) -> Any:
        """Update the status of a report.

        Args:
            report_id (int): ID of the report to update
            status (ReportStatus): New status for the report
            resolved_by (UUID): ID of the admin resolving the report
            resolution_note (str): Note explaining the resolution

        Returns:
            Any: The updated report data

        Note:
            This method should set the resolution timestamp and
            handle any required notifications.
        """

    @abstractmethod
    async def delete_report(self, report_id: int) -> bool:
        """Delete a report.

        Args:
            report_id (int): The ID of the report to delete

        Returns:
            bool: True if deleted successfully
        """