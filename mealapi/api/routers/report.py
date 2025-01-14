"""A module containing report endpoints."""

from typing import Any, List, Optional
from uuid import UUID

from dependency_injector.wiring import inject, Provide
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import jwt

from mealapi.container import Container
from mealapi.core.domain.report import ReportIn, ReportReason, ReportStatus
from mealapi.infrastructure.dto.reportdto import ReportDTO
from mealapi.infrastructure.services.ireport import IReportService
from mealapi.infrastructure.services.iuser import IUserService
from mealapi.infrastructure.utils.consts import SECRET_KEY, ALGORITHM

bearer_scheme = HTTPBearer()
router = APIRouter(
    tags=["report"]
)


@router.post("/create", response_model=ReportDTO)
@inject
async def create_report(
    recipe_id: Optional[int] = Query(None, description="ID of the recipe being reported"),
    comment_id: Optional[int] = Query(None, description="ID of the comment being reported"),
    reason: ReportReason = Query(..., description="Reason for the report"),
    description: str = Query(..., description="Additional details about the report"),
    service: IReportService = Depends(Provide[Container.report_service]),
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)
) -> Any:
    """Create a new report.

    Args:
        recipe_id: ID of the recipe being reported (optional)
        comment_id: ID of the comment being reported (optional)
        reason: Reason for the report
        description: Additional details about the report
        service: The report service (injected)
        credentials: User credentials

    Returns:
        The created report

    Raises:
        HTTPException: If unauthorized or if report creation fails
    """
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        user_uuid = payload.get("sub")
        if not user_uuid:
            raise HTTPException(
                status_code=401,
                detail="Authentication failed: Invalid or missing user ID in token"
            )

        # Validate that at least one of recipe_id or comment_id is provided
        if recipe_id is None and comment_id is None:
            raise HTTPException(
                status_code=400,
                detail="Validation error: At least one of recipe_id or comment_id must be provided"
            )

        # Create the report
        report_data = ReportIn(
            recipe_id=recipe_id,
            comment_id=comment_id,
            reason=reason,
            description=description
        )
        new_report = await service.add_report(report_data, UUID(user_uuid))
        if not new_report:
            raise HTTPException(
                status_code=500,
                detail="Server error: Failed to create report"
            )
        return new_report

    except jwt.JWTError:
        raise HTTPException(
            status_code=401,
            detail="Authentication failed: Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Validation error: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Server error: {str(e)}"
        )


@router.get("/all", response_model=list[ReportDTO])
@inject
async def get_all_reports(
    service: IReportService = Depends(Provide[Container.report_service]),
    user_service: IUserService = Depends(Provide[Container.user_service]),
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> Any:
    """Get all reports in the system.

    Args:
        service: The report service (injected)
        user_service: The user service (injected)
        credentials: User credentials

    Returns:
        list[ReportDTO]: All reports in the system

    Raises:
        HTTPException: If unauthorized or if user is not an admin
    """
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        user_uuid = payload.get("sub")
        if not user_uuid:
            raise HTTPException(
                status_code=401,
                detail="Authentication failed: Invalid or missing user ID in token"
            )

        # Convert user_uuid to UUID object
        user_uuid_obj = UUID(user_uuid)
        is_admin = await user_service.is_admin(user_uuid_obj)
        if not is_admin:
            raise HTTPException(
                status_code=403,
                detail="Access denied: Only administrators can view all reports"
            )

        return await service.get_all_reports()

    except jwt.JWTError:
        raise HTTPException(
            status_code=401,
            detail="Authentication failed: Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Validation error: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Server error: {str(e)}"
        )


@router.get("/my-reports", response_model=List[ReportDTO])
@inject
async def get_my_reports(
    service: IReportService = Depends(Provide[Container.report_service]),
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> List[ReportDTO]:
    """Get all reports made by the authenticated user.

    Args:
        service: The report service (injected)
        credentials: User credentials

    Returns:
        List[ReportDTO]: All reports made by the authenticated user

    Raises:
        HTTPException: If unauthorized
    """
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        user_uuid = payload.get("sub")
        if not user_uuid:
            raise HTTPException(
                status_code=401,
                detail="Authentication failed: Invalid or missing user ID in token"
            )

        reports = await service.get_by_reporter(UUID(user_uuid))
        if not reports:
            return []
        return reports

    except jwt.JWTError:
        raise HTTPException(
            status_code=401,
            detail="Authentication failed: Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Validation error: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Server error: {str(e)}"
        )


@router.get("/", response_model=List[ReportDTO])
@inject
async def get_reports(
    report_id: Optional[int] = None,
    user_id: Optional[UUID] = None,
    status: Optional[ReportStatus] = None,
    comment_id: Optional[int] = None,
    service: IReportService = Depends(Provide[Container.report_service]),
    user_service: IUserService = Depends(Provide[Container.user_service]),
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)
) -> List[ReportDTO]:
    """Get reports with optional filtering.
    
    You can filter reports by various criteria. All filters are optional and can be combined.
    If no filters are provided, returns all reports. Only admins can access this endpoint.

    Args:
        report_id: Filter by specific report ID
        user_id: Filter by reporter's UUID
        status: Filter by report status
        comment_id: Filter by reported comment ID
        service: The report service (injected)
        user_service: The user service (injected)
        credentials: User credentials

    Returns:
        List of matching reports

    Raises:
        HTTPException: If unauthorized or no reports match the criteria
    """
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        user_uuid = payload.get("sub")
        if not user_uuid:
            raise HTTPException(
                status_code=401,
                detail="Authentication failed: Invalid or missing user ID in token"
            )

        if not await user_service.is_admin(user_uuid):
            raise HTTPException(
                status_code=403,
                detail="Access denied: Only administrators can use this endpoint"
            )

        if report_id is not None:
            report = await service.get_by_id(report_id)
            if not report:
                raise HTTPException(
                    status_code=404,
                    detail=f"Not found: Report with ID {report_id} does not exist"
                )
            return [report]

        if user_id:
            reports = await service.get_by_reporter(user_id)
            if not reports:
                raise HTTPException(
                    status_code=404,
                    detail=f"Not found: No reports found for user {user_id}"
                )
            return reports

        if status:
            reports = await service.get_by_status(status)
            if not reports:
                raise HTTPException(
                    status_code=404,
                    detail=f"Not found: No reports found with status {status}"
                )
            return reports

        if comment_id:
            reports = await service.get_by_comment(comment_id)
            if not reports:
                raise HTTPException(
                    status_code=404,
                    detail=f"Not found: No reports found for comment {comment_id}"
                )
            return reports

        reports = await service.get_all_reports()
        return reports

    except jwt.JWTError:
        raise HTTPException(
            status_code=401,
            detail="Authentication failed: Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Validation error: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Server error: {str(e)}"
        )


@router.put("/{report_id}/status", response_model=ReportDTO)
@inject
async def update_report_status(
    report_id: int,
    status: ReportStatus,
    resolution_note: str | None = None,
    service: IReportService = Depends(Provide[Container.report_service]),
    user_service: IUserService = Depends(Provide[Container.user_service]),
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> ReportDTO:
    """Update a report's status.

    Args:
        report_id: The ID of the report to update
        status: The new status
        resolution_note: Optional note explaining the resolution
        service: The report service (injected)
        user_service: The user service (injected)
        credentials: User credentials

    Returns:
        The updated report

    Raises:
        HTTPException: If unauthorized or report not found
    """
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        user_uuid = payload.get("sub")
        if not user_uuid:
            raise HTTPException(
                status_code=401,
                detail="Authentication failed: Invalid or missing user ID in token"
            )

        if not await user_service.is_admin(user_uuid):
            raise HTTPException(
                status_code=403,
                detail="Access denied: Only administrators can update report status"
            )

        updated_report = await service.update_report_status(report_id, status, UUID(user_uuid), resolution_note)
        if not updated_report:
            raise HTTPException(
                status_code=404,
                detail=f"Not found: Report with ID {report_id} does not exist"
            )
        
        return updated_report

    except jwt.JWTError:
        raise HTTPException(
            status_code=401,
            detail="Authentication failed: Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Validation error: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Server error: {str(e)}"
        )


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
        report_id: The ID of the report to delete
        service: The report service (injected)
        user_service: The user service (injected)
        credentials: User credentials

    Raises:
        HTTPException: If unauthorized or report not found
    """
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        user_uuid = payload.get("sub")
        if not user_uuid:
            raise HTTPException(
                status_code=401,
                detail="Authentication failed: Invalid or missing user ID in token"
            )

        if not await user_service.is_admin(user_uuid):
            raise HTTPException(
                status_code=403,
                detail="Access denied: Only administrators can delete reports"
            )

        if not await service.delete_report(report_id):
            raise HTTPException(
                status_code=404,
                detail=f"Not found: Report with ID {report_id} does not exist"
            )

    except jwt.JWTError:
        raise HTTPException(
            status_code=401,
            detail="Authentication failed: Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Validation error: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Server error: {str(e)}"
        )
