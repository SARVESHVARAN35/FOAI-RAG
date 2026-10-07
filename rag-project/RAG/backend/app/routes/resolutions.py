from fastapi import APIRouter, Depends, HTTPException

from app.core.security import get_current_user, require_roles
from app.db.database import get_connection
from app.schemas.auth import CurrentUser

router = APIRouter(
    prefix="/resolutions",
    tags=["Resolutions"]
)


@router.post("/{incident_id}")
def create_resolution(
    incident_id: int,
    root_cause: str,
    resolution_description: str,
    steps_taken: str,
    additional_notes: str = "",
    current_user: CurrentUser = Depends(
        require_roles("SUPPORT_ENGINEER", "IT_LEAD", "ADMIN")
    )
):
    connection = get_connection()

    try:
        with connection.cursor() as cursor:

            # Check incident exists
            cursor.execute(
                """
                SELECT id, created_by
                FROM incidents
                WHERE id = %s
                """,
                (incident_id,)
            )

            incident = cursor.fetchone()

            if not incident:
                raise HTTPException(
                    status_code=404,
                    detail="Incident not found"
                )

            if (
                current_user["role"] == "SUPPORT_ENGINEER"
                and incident[1] != current_user["id"]
            ):
                raise HTTPException(
                    status_code=403,
                    detail="You do not have permission to submit a resolution for this incident."
                )

            # Create resolution
            cursor.execute(
                """
                INSERT INTO resolutions
                (
                    incident_id,
                    root_cause,
                    resolution_description,
                    steps_taken,
                    additional_notes,
                    submitted_by,
                    status
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING id, incident_id, root_cause,
                          resolution_description, steps_taken,
                          additional_notes, submitted_by,
                          status, reviewed_by, review_comment,
                          created_at, reviewed_at
                """,
                (
                    incident_id,
                    root_cause,
                    resolution_description,
                    steps_taken,
                    additional_notes,
                    current_user["id"],
                    "PENDING_REVIEW"
                )
            )

            resolution = cursor.fetchone()

            # Mark incident as resolved
            cursor.execute(
                """
                UPDATE incidents
                SET status = %s,
                    resolved_at = CURRENT_TIMESTAMP,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = %s
                """,
                ("RESOLVED", incident_id)
            )

            connection.commit()

            return {
                "id": resolution[0],
                "incident_id": resolution[1],
                "root_cause": resolution[2],
                "resolution_description": resolution[3],
                "steps_taken": resolution[4],
                "additional_notes": resolution[5],
                "submitted_by": resolution[6],
                "status": resolution[7],
                "reviewed_by": resolution[8],
                "review_comment": resolution[9],
                "created_at": resolution[10],
                "reviewed_at": resolution[11]
            }

    finally:
        connection.close()


@router.get("/{incident_id}")
def get_resolution(
    incident_id: int,
    current_user: CurrentUser = Depends(get_current_user)
):
    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            if current_user["role"] == "SUPPORT_ENGINEER":
                cursor.execute(
                    """
                    SELECT created_by
                    FROM incidents
                    WHERE id = %s
                    """,
                    (incident_id,)
                )
                incident = cursor.fetchone()
                if incident is None:
                    raise HTTPException(
                        status_code=404,
                        detail="Incident not found"
                    )
                if incident[0] != current_user["id"]:
                    raise HTTPException(
                        status_code=403,
                        detail="You do not have permission to view this incident's resolutions."
                    )

                cursor.execute(
                    """
                    SELECT id, incident_id, root_cause,
                           resolution_description, steps_taken,
                           additional_notes, submitted_by,
                           status, reviewed_by, review_comment,
                           created_at, reviewed_at
                    FROM resolutions
                    WHERE incident_id = %s AND submitted_by = %s
                    ORDER BY created_at DESC
                    """,
                    (incident_id, current_user["id"])
                )
            else:
                cursor.execute(
                    """
                    SELECT id, incident_id, root_cause,
                           resolution_description, steps_taken,
                           additional_notes, submitted_by,
                           status, reviewed_by, review_comment,
                           created_at, reviewed_at
                    FROM resolutions
                    WHERE incident_id = %s
                    ORDER BY created_at DESC
                    """,
                    (incident_id,)
                )

            rows = cursor.fetchall()

            return [
                {
                    "id": row[0],
                    "incident_id": row[1],
                    "root_cause": row[2],
                    "resolution_description": row[3],
                    "steps_taken": row[4],
                    "additional_notes": row[5],
                    "submitted_by": row[6],
                    "status": row[7],
                    "reviewed_by": row[8],
                    "review_comment": row[9],
                    "created_at": row[10],
                    "reviewed_at": row[11]
                }
                for row in rows
            ]

    finally:
        connection.close()