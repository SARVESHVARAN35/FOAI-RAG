from fastapi import APIRouter, Depends, HTTPException

from app.core.security import get_current_user, require_roles
from app.db.database import get_connection
from app.schemas.auth import CurrentUser

router = APIRouter(prefix="/incidents", tags=["Incidents"])
ALL_ROLES = ("SUPPORT_ENGINEER", "IT_LEAD", "ADMIN")


@router.post("/")
def create_incident(
    title: str,
    error_code: str,
    service: str,
    description: str,
    current_user: CurrentUser = Depends(require_roles(*ALL_ROLES))
):
    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO incidents
                (title, error_code, service, description, status, created_by)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING id, title, error_code, service,
                          description, status, created_by,
                          created_at, updated_at, resolved_at
                """,
                (
                    title,
                    error_code,
                    service,
                    description,
                    "OPEN",
                    current_user["id"]
                )
            )

            incident = cursor.fetchone()
            connection.commit()

            return {
                "id": incident[0],
                "title": incident[1],
                "error_code": incident[2],
                "service": incident[3],
                "description": incident[4],
                "status": incident[5],
                "created_by": incident[6],
                "created_at": incident[7],
                "updated_at": incident[8],
                "resolved_at": incident[9]
            }

    finally:
        connection.close()


@router.get("/")
def get_incidents(
    current_user: CurrentUser = Depends(get_current_user)
):
    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            if current_user["role"] == "SUPPORT_ENGINEER":
                cursor.execute(
                    """
                    SELECT id, title, error_code, service,
                           description, status, created_by,
                           created_at, updated_at, resolved_at
                    FROM incidents
                    WHERE created_by = %s
                    ORDER BY created_at DESC
                    """,
                    (current_user["id"],)
                )
            else:
                cursor.execute(
                    """
                    SELECT id, title, error_code, service,
                           description, status, created_by,
                           created_at, updated_at, resolved_at
                    FROM incidents
                    ORDER BY created_at DESC
                    """
                )

            rows = cursor.fetchall()

            return [
                {
                    "id": row[0],
                    "title": row[1],
                    "error_code": row[2],
                    "service": row[3],
                    "description": row[4],
                    "status": row[5],
                    "created_by": row[6],
                    "created_at": row[7],
                    "updated_at": row[8],
                    "resolved_at": row[9]
                }
                for row in rows
            ]

    finally:
        connection.close()


@router.get("/{incident_id}")
def get_incident(
    incident_id: int,
    current_user: CurrentUser = Depends(get_current_user)
):
    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT id, title, error_code, service,
                       description, status, created_by,
                       created_at, updated_at, resolved_at
                FROM incidents
                WHERE id = %s
                """,
                (incident_id,)
            )

            row = cursor.fetchone()

            if not row:
                raise HTTPException(
                    status_code=404,
                    detail="Incident not found"
                )

            if (
                current_user["role"] == "SUPPORT_ENGINEER"
                and row[6] != current_user["id"]
            ):
                raise HTTPException(
                    status_code=403,
                    detail="You do not have permission to view this incident."
                )

            return {
                "id": row[0],
                "title": row[1],
                "error_code": row[2],
                "service": row[3],
                "description": row[4],
                "status": row[5],
                "created_by": row[6],
                "created_at": row[7],
                "updated_at": row[8],
                "resolved_at": row[9]
            }

    finally:
        connection.close()


@router.put("/{incident_id}")
def update_incident(
    incident_id: int,
    title: str,
    error_code: str,
    service: str,
    description: str,
    status: str,
    current_user: CurrentUser = Depends(require_roles(*ALL_ROLES))
):
    allowed_statuses = {"OPEN", "IN_PROGRESS", "RESOLVED", "CLOSED"}
    status = status.upper()

    if status not in allowed_statuses:
        raise HTTPException(
            status_code=400,
            detail="Invalid status. Use OPEN, IN_PROGRESS, RESOLVED, or CLOSED."
        )

    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT created_by
                FROM incidents
                WHERE id = %s
                FOR UPDATE
                """,
                (incident_id,)
            )
            owner = cursor.fetchone()

            if owner is None:
                raise HTTPException(
                    status_code=404,
                    detail="Incident not found"
                )
            if (
                current_user["role"] == "SUPPORT_ENGINEER"
                and owner[0] != current_user["id"]
            ):
                raise HTTPException(
                    status_code=403,
                    detail="You do not have permission to modify this incident."
                )

            cursor.execute(
                """
                UPDATE incidents
                SET title = %s,
                    error_code = %s,
                    service = %s,
                    description = %s,
                    status = %s,
                    resolved_at = CASE
                        WHEN %s = 'RESOLVED' THEN
                            COALESCE(resolved_at, CURRENT_TIMESTAMP)
                        ELSE NULL
                    END,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = %s
                RETURNING id, title, error_code, service,
                          description, status, created_by,
                          created_at, updated_at, resolved_at
                """,
                (
                    title,
                    error_code,
                    service,
                    description,
                    status,
                    status,
                    incident_id
                )
            )

            incident = cursor.fetchone()

            if not incident:
                raise HTTPException(
                    status_code=404,
                    detail="Incident not found"
                )

            connection.commit()

            return {
                "id": incident[0],
                "title": incident[1],
                "error_code": incident[2],
                "service": incident[3],
                "description": incident[4],
                "status": incident[5],
                "created_by": incident[6],
                "created_at": incident[7],
                "updated_at": incident[8],
                "resolved_at": incident[9]
            }

    finally:
        connection.close()


@router.delete("/{incident_id}")
def delete_incident(
    incident_id: int,
    _admin: CurrentUser = Depends(require_roles("ADMIN"))
):
    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                DELETE FROM incidents
                WHERE id = %s
                RETURNING id
                """,
                (incident_id,)
            )

            deleted = cursor.fetchone()

            if not deleted:
                raise HTTPException(
                    status_code=404,
                    detail="Incident not found"
                )

            connection.commit()

            return {
                "message": "Incident deleted successfully",
                "id": deleted[0]
            }

    finally:
        connection.close()