from fastapi import APIRouter, Depends, HTTPException

from app.core.security import require_roles
from app.db.database import get_connection
from app.schemas.auth import CurrentUser


router = APIRouter(
    prefix="/reviews",
    tags=["Reviews"]
)


@router.get("/pending")
def get_pending_reviews(
    reviewer: CurrentUser = Depends(require_roles("IT_LEAD", "ADMIN"))
):
    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    r.id,
                    r.incident_id,
                    r.root_cause,
                    r.resolution_description,
                    r.steps_taken,
                    r.additional_notes,
                    r.submitted_by,
                    r.status,
                    r.reviewed_by,
                    r.review_comment,
                    r.created_at,
                    r.reviewed_at
                FROM resolutions r
                WHERE r.status = 'PENDING_REVIEW'
                  AND (%s = 'ADMIN' OR r.submitted_by <> %s)
                ORDER BY r.created_at ASC
                """,
                (reviewer["role"], reviewer["id"]),
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


@router.post("/{resolution_id}")
def review_resolution(
    resolution_id: int,
    action: str,
    review_comment: str = "",
    current_user: CurrentUser = Depends(
        require_roles("IT_LEAD", "ADMIN")
    )
):
    allowed_actions = {
        "APPROVED",
        "REJECTED",
        "CHANGES_REQUESTED"
    }

    action = action.upper()

    if action not in allowed_actions:
        raise HTTPException(
            status_code=400,
            detail=(
                "Invalid action. Use APPROVED, "
                "REJECTED, or CHANGES_REQUESTED."
            )
        )

    connection = get_connection()

    try:
        with connection.cursor() as cursor:

            # Check resolution exists and is pending
            cursor.execute(
                """
                SELECT id, incident_id, status, submitted_by
                FROM resolutions
                WHERE id = %s
                """,
                (resolution_id,)
            )

            resolution = cursor.fetchone()

            if not resolution:
                raise HTTPException(
                    status_code=404,
                    detail="Resolution not found"
                )

            if resolution[2] != "PENDING_REVIEW":
                raise HTTPException(
                    status_code=400,
                    detail=(
                        f"Resolution is already {resolution[2]} "
                        "and cannot be reviewed again."
                    )
                )

            if resolution[3] == current_user["id"]:
                raise HTTPException(
                    status_code=403,
                    detail="You cannot review your own resolution.",
                )

            incident_id = resolution[1]

            # Update review status
            cursor.execute(
                """
                UPDATE resolutions
                SET status = %s,
                    reviewed_by = %s,
                    review_comment = %s,
                    reviewed_at = CURRENT_TIMESTAMP
                WHERE id = %s
                RETURNING id, incident_id, status,
                          reviewed_by, review_comment,
                          reviewed_at
                """,
                (
                    action,
                    current_user["id"],
                    review_comment,
                    resolution_id
                )
            )

            result = cursor.fetchone()

            connection.commit()

            response = {
                "id": result[0],
                "incident_id": result[1],
                "status": result[2],
                "reviewed_by": result[3],
                "review_comment": result[4],
                "reviewed_at": result[5]
            }

            # --------------------------------------------------
            # APPROVED RESOLUTION -> RAG KNOWLEDGE
            # --------------------------------------------------

            if action == "APPROVED":
                from app.rag.resolution_ingestion import ingest_approved_resolution

                # Get the actual resolution + incident data
                cursor.execute(
                    """
                    SELECT
                        r.id,
                        r.root_cause,
                        r.resolution_description,
                        r.steps_taken,
                        r.additional_notes,
                        i.title,
                        i.error_code,
                        i.service
                    FROM resolutions r
                    JOIN incidents i
                        ON r.incident_id = i.id
                    WHERE r.id = %s
                    """,
                    (resolution_id,)
                )

                resolution_data = cursor.fetchone()

                if not resolution_data:
                    raise HTTPException(
                        status_code=404,
                        detail=(
                            "Approved resolution or "
                            "incident data not found."
                        )
                    )

                (
                    db_resolution_id,
                    root_cause,
                    resolution_description,
                    steps_taken,
                    additional_notes,
                    incident_title,
                    error_code,
                    service
                ) = resolution_data

                # Index the approved resolution
                ingestion_result = ingest_approved_resolution(
                    resolution_id=db_resolution_id,
                    incident_title=incident_title,
                    error_code=error_code,
                    service=service,
                    root_cause=root_cause,
                    resolution_description=resolution_description,
                    steps_taken=steps_taken,
                    additional_notes=additional_notes
                )

                response["knowledge_ingestion"] = ingestion_result

            return response

    finally:
        connection.close()