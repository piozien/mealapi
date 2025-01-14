"""Module containing report repository implementation."""

from typing import Any, Iterable
from datetime import datetime, timezone
from sqlalchemy import select, insert

from uuid import UUID

from mealapi.core.repositories.ireport import IReportRepository
from mealapi.core.domain.report import ReportIn, Report, ReportStatus
from mealapi.infrastructure.dto.reportdto import ReportDTO
from mealapi.db import report_table, comment_table, database


class ReportRepository(IReportRepository):
    """A class representing report DB repository."""

    async def get_all_reports(self) -> Iterable[Any]:
        """Get all reports.

        Returns:
            Iterable[Any]: All reports in the system

        """
        query = (
            select(
                report_table.c.id,
                report_table.c.reporter_id,
                report_table.c.recipe_id,
                report_table.c.comment_id,
                report_table.c.reason,
                report_table.c.description,
                report_table.c.created_at,
                report_table.c.status,
                report_table.c.resolved_by,
                report_table.c.resolution_note,
                report_table.c.resolved_at,
                comment_table.c.id.label('comment_id'),
                comment_table.c.content.label('comment_content'),
                comment_table.c.author.label('comment_author_id'),
                comment_table.c.created_at.label('comment_created_at'),
                comment_table.c.rating_id.label('comment_rating'),
            )
            .select_from(
                report_table.outerjoin(
                    comment_table,
                    report_table.c.comment_id == comment_table.c.id
                )
            )
            .order_by(report_table.c.created_at.desc())
        )
        reports = await database.fetch_all(query)
        return [ReportDTO.from_record(report) for report in reports]

    async def get_by_status(self, status: ReportStatus) -> Iterable[Any]:
        """Get all reports with a specific status.

        Args:
            status (ReportStatus): The status to filter by

        Returns:
            Iterable[Any]: All reports with the status
        """
        query = (
            select(
                report_table.c.id,
                report_table.c.reporter_id,
                report_table.c.recipe_id,
                report_table.c.comment_id,
                report_table.c.reason,
                report_table.c.description,
                report_table.c.created_at,
                report_table.c.status,
                report_table.c.resolved_by,
                report_table.c.resolution_note,
                report_table.c.resolved_at,
                comment_table.c.id.label('comment_id'),
                comment_table.c.content.label('comment_content'),
                comment_table.c.author.label('comment_author_id'),
                comment_table.c.created_at.label('comment_created_at'),
                comment_table.c.rating_id.label('comment_rating'),
            )
            .select_from(
                report_table.outerjoin(
                    comment_table,
                    report_table.c.comment_id == comment_table.c.id
                )
            )
            .where(report_table.c.status == status)
            .order_by(report_table.c.created_at.desc())
        )
        reports = await database.fetch_all(query)
        return [ReportDTO.from_record(report) for report in reports]

    async def get_by_comment(self, comment_id: int) -> Iterable[Any]:
        """Get all reports for a specific comment.

        Args:
            comment_id (int): The ID of the comment

        Returns:
            Iterable[Any]: All reports for the comment
        """
        query = (
            select(
                report_table.c.id,
                report_table.c.reporter_id,
                report_table.c.recipe_id,
                report_table.c.comment_id,
                report_table.c.reason,
                report_table.c.description,
                report_table.c.created_at,
                report_table.c.status,
                report_table.c.resolved_by,
                report_table.c.resolution_note,
                report_table.c.resolved_at,
                comment_table.c.id.label('comment_id'),
                comment_table.c.content.label('comment_content'),
                comment_table.c.author.label('comment_author_id'),
                comment_table.c.created_at.label('comment_created_at'),
                comment_table.c.rating_id.label('comment_rating'),
            )
            .select_from(report_table.join(comment_table, report_table.c.comment_id == comment_table.c.id))
            .where(report_table.c.comment_id == comment_id)
            .order_by(report_table.c.created_at.desc())
        )
        reports = await database.fetch_all(query)
        return [ReportDTO.from_record(report) for report in reports]

    async def get_by_reporter(self, reporter_id: UUID) -> Iterable[Any]:
        """Get all reports made by a specific user.

        Args:
            reporter_id (UUID): The ID of the reporter

        Returns:
            Iterable[Any]: All reports made by the reporter
        """
        query = (
            select(
                report_table.c.id,
                report_table.c.reporter_id,
                report_table.c.recipe_id,
                report_table.c.comment_id,
                report_table.c.reason,
                report_table.c.description,
                report_table.c.created_at,
                report_table.c.status,
                report_table.c.resolved_by,
                report_table.c.resolution_note,
                report_table.c.resolved_at,
                comment_table.c.id.label('comment_id'),
                comment_table.c.content.label('comment_content'),
                comment_table.c.author.label('comment_author_id'),
                comment_table.c.created_at.label('comment_created_at'),
                comment_table.c.rating_id.label('comment_rating'),
            )
            .select_from(
                report_table.outerjoin(
                    comment_table,
                    report_table.c.comment_id == comment_table.c.id
                )
            )
            .where(report_table.c.reporter_id == reporter_id)
            .order_by(report_table.c.created_at.desc())
        )
        reports = await database.fetch_all(query)
        return [ReportDTO.from_record(report) for report in reports]

    async def get_by_id(self, report_id: int) -> Report | None:
        """Get a report by its ID.

        Args:
            report_id (int): The ID of the report

        Returns:
            Report | None: The report if found
        """
        query = (
            select(report_table)
            .where(report_table.c.id == report_id)
        )
        result = await database.fetch_one(query)
        return Report(**dict(result)) if result else None

    async def add_report(self, report: ReportIn, reporter_id: UUID) -> ReportDTO | None:
        """Add a new report.

        Args:
            report (ReportIn): The report to add
            reporter_id (UUID): ID of the user creating the report

        Returns:
            ReportDTO | None: The newly created report
        """
        query = insert(report_table).values(
            recipe_id=report.recipe_id,
            comment_id=report.comment_id,
            reporter_id=reporter_id,
            reason=report.reason,
            description=report.description,
            status=ReportStatus.PENDING,
            created_at=datetime.now(timezone.utc)
        ).returning(report_table)

        result = await database.fetch_one(query)
        if result:
            return ReportDTO.from_record(result)
        return None

    async def update_status(
        self,
        report_id: int,
        status: ReportStatus,
        resolved_by: UUID | None = None,
        resolution_note: str | None = None,
    ) -> Any | None:
        """Update a report's status.

        Args:
            report_id (int): The ID of the report to update
            status (ReportStatus): The new status
            resolved_by (UUID | None): ID of the admin who resolved the report
            resolution_note (str | None): Note explaining the resolution

        Returns:
            Any | None: The updated report
        """
        if await self.get_by_id(report_id):
            update_data = {
                "status": status,
                "resolved_at": datetime.now(timezone.utc).replace(tzinfo=None) if status in [ReportStatus.RESOLVED,
                                                                                    ReportStatus.REJECTED] else None,
            }
            
            if status in [ReportStatus.RESOLVED, ReportStatus.REJECTED]:
                update_data["resolved_by"] = resolved_by
                update_data["resolution_note"] = resolution_note

            query = (
                report_table.update()
                .where(report_table.c.id == report_id)
                .values(**update_data)
            )
            await database.execute(query)
            return await self.get_by_id(report_id)

        return None

    async def delete_report(self, report_id: int) -> bool:
        """Delete a report.

        Args:
            report_id (int): The ID of the report to delete

        Returns:
            bool: True if report was deleted, False if report was not found
        """
        if await self.get_by_id(report_id):
            query = report_table.delete().where(report_table.c.id == report_id)
            await database.execute(query)
            return True

        return False
