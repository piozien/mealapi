"""A module containing report endpoints."""

from typing import Iterable, Any

from dependency_injector.wiring import inject, Provide
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import jwt
from uuid import UUID

from mealapi.infrastructure.utils.consts import SECRET_KEY, ALGORITHM
from mealapi.container import Container
from mealapi.core.domain.report import ReportIn, ReportStatus
from mealapi.infrastructure.dto.reportdto import ReportDTO
from mealapi.infrastructure.services.ireport import IReportService
from mealapi.infrastructure.services.iuser import IUserService
from mealapi.core.domain.user import UserRole

bearer_scheme = HTTPBearer()
router = APIRouter(
    tags=["report"],
    responses={
        401: {"description": "Unauthorized"},
        403: {"description": "Forbidden - insufficient permissions"},
        404: {"description": "Not Found"},
    }
)


async def is_admin(user_uuid: str, user_service: IUserService) -> bool:
    """Check if the user has admin role.

    Args:
        user_uuid (str): The UUID of the user to check
        user_service (IUserService): The user service instance

    Returns:
        bool: True if user is admin, False otherwise
    """
    user = await user_service.get_by_uuid(user_uuid)
    return user is not None and user.role == UserRole.ADMIN


@router.post("/create", response_model=ReportDTO, status_code=status.HTTP_201_CREATED)
@inject
async def create_report(
    report: ReportIn,
    service: IReportService = Depends(Provide[Container.report_service]),
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> ReportDTO:
    """Create a new content report.

    Used to report inappropriate content, spam, or incorrect information.

    Args:
        report (ReportIn): Report details

    Example request body:
        {
            "recipe_id": 1,  # ID of the reported recipe (optional if reporting a comment)
            "comment_id": 2,  # ID of the reported comment (optional if reporting a recipe)
            "reason": "INAPPROPRIATE",  # One of: SPAM, INAPPROPRIATE, INCORRECT, OTHER
            "description": "This recipe contains offensive language"
        }

    Returns:
        ReportDTO: Created report with metadata

    Raises:
        HTTPException:
            - 401: Unauthorized (missing or invalid token)
            - 400: Invalid report data or missing required fields
    """
    try:
        token = credentials.credentials
        token_payload = jwt.decode(
            token,
            key=SECRET_KEY,
            algorithms=[ALGORITHM],
        )
        user_uuid = token_payload.get("sub")

        if not user_uuid:
            raise HTTPException(status_code=401, detail="Could not validate credentials")

        new_report = await service.add_report(report, UUID(user_uuid))
        if new_report is None:
            raise HTTPException(status_code=400, detail="Could not create report")
        return new_report.model_dump() if new_report else {}

    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Could not validate credentials")


@router.get("/comment/{comment_id}", response_model=list[ReportDTO], status_code=200)
@inject
async def get_comment_reports(
    comment_id: int,
    service: IReportService = Depends(Provide[Container.report_service]),
    user_service: IUserService = Depends(Provide[Container.user_service]),
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> Iterable[ReportDTO]:
    """Get all reports for a comment.

    Args:
        comment_id (int): The ID of the comment.

    Returns:
        Iterable[ReportDTO]: All reports for the comment.

    Raises:
        HTTPException:
            - 401: Unauthorized (missing or invalid token)
            - 403: Forbidden (not an admin)
    """
    try:
        token = credentials.credentials
        token_payload = jwt.decode(
            token,
            key=SECRET_KEY,
            algorithms=[ALGORITHM],
        )
        user_uuid = token_payload.get("sub")

        if not user_uuid:
            raise HTTPException(status_code=401, detail="Could not validate credentials")

        # Only admins can view reports
        if not await is_admin(user_uuid, user_service):
            raise HTTPException(status_code=403, detail="Unauthorized - Admin access required")

        return await service.get_by_comment(comment_id)

    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Could not validate credentials")


@router.get("/user/{user_id}", response_model=list[ReportDTO], status_code=200)
@inject
async def get_user_reports(
    user_id: UUID,
    service: IReportService = Depends(Provide[Container.report_service]),
    user_service: IUserService = Depends(Provide[Container.user_service]),
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> Iterable[ReportDTO]:
    """Get all reports by a user.

    Args:
        user_id (UUID): The ID of the user.

    Returns:
        Iterable[ReportDTO]: All reports by the user.

    Raises:
        HTTPException:
            - 401: Unauthorized (missing or invalid token)
            - 403: Forbidden (not the user or not an admin)
    """
    try:
        token = credentials.credentials
        token_payload = jwt.decode(
            token,
            key=SECRET_KEY,
            algorithms=[ALGORITHM],
        )
        current_user_uuid = token_payload.get("sub")

        if not current_user_uuid:
            raise HTTPException(status_code=401, detail="Could not validate credentials")

        # Allow viewing if it's the user's own reports or if they're an admin
        if str(user_id) != current_user_uuid and not await is_admin(current_user_uuid, user_service):
            raise HTTPException(status_code=403, detail="Unauthorized")

        return await service.get_by_reporter(user_id)

    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Could not validate credentials")


@router.get("/status/{status}", response_model=list[ReportDTO], status_code=200)
@inject
async def get_reports_by_status(
    status: ReportStatus,
    service: IReportService = Depends(Provide[Container.report_service]),
    user_service: IUserService = Depends(Provide[Container.user_service]),
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> Iterable[ReportDTO]:
    """Get all reports with a specific status.

    Args:
        status (ReportStatus): The status to filter by.

    Returns:
        Iterable[ReportDTO]: All reports with the given status.

    Raises:
        HTTPException:
            - 401: Unauthorized (missing or invalid token)
            - 403: Forbidden (not an admin)
    """
    try:
        token = credentials.credentials
        token_payload = jwt.decode(
            token,
            key=SECRET_KEY,
            algorithms=[ALGORITHM],
        )
        user_uuid = token_payload.get("sub")

        if not user_uuid:
            raise HTTPException(status_code=401, detail="Could not validate credentials")

        # Only admins can view reports by status
        if not await is_admin(user_uuid, user_service):
            raise HTTPException(status_code=403, detail="Unauthorized - Admin access required")

        return await service.get_by_status(status)

    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Could not validate credentials")


@router.get("/all", response_model=list[ReportDTO], status_code=200)
@inject
async def get_all_reports(
    service: IReportService = Depends(Provide[Container.report_service]),
    user_service: IUserService = Depends(Provide[Container.user_service]),
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> Iterable[ReportDTO]:
    """Get all reports in the system.

    Args:
        service (IReportService): The injected service dependency.
        user_service (IUserService): The injected user service dependency.
        credentials (HTTPAuthorizationCredentials): The credentials.

    Returns:
        Iterable[ReportDTO]: All reports in the system.

    Raises:
        HTTPException:
            - 401: Unauthorized (missing or invalid token)
            - 403: Forbidden (not an admin)
    """
    try:
        token = credentials.credentials
        token_payload = jwt.decode(
            token,
            key=SECRET_KEY,
            algorithms=[ALGORITHM],
        )
        user_uuid = token_payload.get("sub")

        if not user_uuid:
            raise HTTPException(status_code=401, detail="Could not validate credentials")

        if not await is_admin(user_uuid, user_service):
            raise HTTPException(status_code=403, detail="Only admins can view all reports")

        reports = await service.get_all()
        return [report.model_dump() for report in reports]

    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Could not validate credentials")


@router.put("/{report_id}/status", response_model=ReportDTO, status_code=200)
@inject
async def update_report_status(
    report_id: int,
    status: ReportStatus,
    resolution_note: str | None = None,
    service: IReportService = Depends(Provide[Container.report_service]),
    user_service: IUserService = Depends(Provide[Container.user_service]),
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> Any:
    """Update a report's status.

    Args:
        report_id (int): The ID of the report.
        status (ReportStatus): The new status.
        resolution_note (str | None): Note explaining the resolution.
        service (IReportService): The injected service dependency.
        user_service (IUserService): The injected user service dependency.
        credentials (HTTPAuthorizationCredentials): The credentials.

    Returns:
        dict: The updated report attributes.

    Raises:
        HTTPException:
            - 401: Unauthorized (missing or invalid token)
            - 403: Forbidden (not an admin)
            - 404: Report not found
    """
    try:
        token = credentials.credentials
        token_payload = jwt.decode(
            token,
            key=SECRET_KEY,
            algorithms=[ALGORITHM],
        )
        user_uuid = token_payload.get("sub")

        if not user_uuid:
            raise HTTPException(status_code=401, detail="Could not validate credentials")

        if not await is_admin(user_uuid, user_service):
            raise HTTPException(status_code=403, detail="Only admins can update report status")

        report = await service.update_status(
            report_id,
            status,
            resolved_by=UUID(user_uuid) if status in [ReportStatus.RESOLVED, ReportStatus.REJECTED] else None,
            resolution_note=resolution_note if status in [ReportStatus.RESOLVED, ReportStatus.REJECTED] else None,
        )
        if report is None:
            raise HTTPException(status_code=404, detail="Report not found")
        return report.model_dump()

    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Could not validate credentials")


@router.delete("/{report_id}", status_code=204)
@inject
async def delete_report(
    report_id: int,
    service: IReportService = Depends(Provide[Container.report_service]),
    user_service: IUserService = Depends(Provide[Container.user_service]),
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> None:
    """Delete a report.

    Args:
        report_id (int): The ID of the report.
        service (IReportService): The injected service dependency.
        user_service (IUserService): The injected user service dependency.
        credentials (HTTPAuthorizationCredentials): The credentials.

    Raises:
        HTTPException:
            - 401: Unauthorized (missing or invalid token)
            - 403: Forbidden (not an admin)
            - 404: Report not found
    """
    try:
        token = credentials.credentials
        token_payload = jwt.decode(
            token,
            key=SECRET_KEY,
            algorithms=[ALGORITHM],
        )
        user_uuid = token_payload.get("sub")

        if not user_uuid:
            raise HTTPException(status_code=401, detail="Could not validate credentials")

        # Only admins can delete reports
        if not await is_admin(user_uuid, user_service):
            raise HTTPException(status_code=403, detail="Unauthorized - Admin access required")

        if await service.delete_report(report_id):
            return

        raise HTTPException(status_code=404, detail="Report not found")

    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Could not validate credentials")
