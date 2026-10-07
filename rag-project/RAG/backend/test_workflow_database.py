"""Read-only checks for Incident -> Resolution -> Review database storage."""

import os
import sys

# The verifier does not use DEBUG; keep this unrelated setting from blocking DB checks.
os.environ["DEBUG"] = "false"

import psycopg

from app.db.database import get_connection


REQUIRED_COLUMNS = {
    "users": {"id", "role"},
    "incidents": {
        "id",
        "title",
        "error_code",
        "service",
        "description",
        "status",
        "created_by",
        "created_at",
        "updated_at",
        "resolved_at",
    },
    "resolutions": {
        "id",
        "incident_id",
        "root_cause",
        "resolution_description",
        "steps_taken",
        "additional_notes",
        "submitted_by",
        "status",
        "reviewed_by",
        "review_comment",
        "created_at",
        "reviewed_at",
    },
}

REQUIRED_FOREIGN_KEYS = {
    ("incidents", "created_by", "users", "id"),
    ("resolutions", "incident_id", "incidents", "id"),
    ("resolutions", "submitted_by", "users", "id"),
    ("resolutions", "reviewed_by", "users", "id"),
}


def report(label: str, passed: bool, detail: str = "") -> bool:
    result = "PASS" if passed else "FAIL"
    suffix = f" - {detail}" if detail else ""
    print(f"{result}: {label}{suffix}")
    return passed


def fetch_dicts(cursor: psycopg.Cursor) -> list[dict[str, object]]:
    columns = [column.name for column in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]


def print_records(label: str, rows: list[dict[str, object]]) -> None:
    print(f"\n{label}")
    if not rows:
        print("(no records)")
        return
    for row in rows:
        print(row)


def main() -> int:
    checks: list[bool] = []
    try:
        connection = get_connection()
    except Exception as error:
        report("Database connection", False, f"{type(error).__name__}: {error}")
        return 1

    try:
        with connection.cursor() as cursor:
            cursor.execute("SET TRANSACTION READ ONLY")
            cursor.execute("SELECT current_database()")
            database_name = cursor.fetchone()[0]
            checks.append(
                report(
                    "Connected to FOAI",
                    database_name == "FOAI",
                    f"connected database: {database_name}",
                )
            )

            cursor.execute(
                """
                SELECT table_name, column_name
                FROM information_schema.columns
                WHERE table_schema = 'public'
                  AND table_name = ANY(%s)
                """,
                (list(REQUIRED_COLUMNS),),
            )
            actual_columns: dict[str, set[str]] = {}
            for table_name, column_name in cursor.fetchall():
                actual_columns.setdefault(table_name, set()).add(column_name)

            table_ready: dict[str, bool] = {}
            for table_name, expected in REQUIRED_COLUMNS.items():
                missing = expected - actual_columns.get(table_name, set())
                table_ready[table_name] = not missing
                checks.append(
                    report(
                        f"{table_name} required columns",
                        not missing,
                        "all present" if not missing else f"missing: {sorted(missing)}",
                    )
                )

            cursor.execute(
                """
                SELECT
                    tc.table_name,
                    kcu.column_name,
                    ccu.table_name AS foreign_table_name,
                    ccu.column_name AS foreign_column_name
                FROM information_schema.table_constraints AS tc
                JOIN information_schema.key_column_usage AS kcu
                  ON tc.constraint_catalog = kcu.constraint_catalog
                 AND tc.constraint_schema = kcu.constraint_schema
                 AND tc.constraint_name = kcu.constraint_name
                JOIN information_schema.constraint_column_usage AS ccu
                  ON tc.constraint_catalog = ccu.constraint_catalog
                 AND tc.constraint_schema = ccu.constraint_schema
                 AND tc.constraint_name = ccu.constraint_name
                WHERE tc.constraint_type = 'FOREIGN KEY'
                  AND tc.constraint_schema = 'public'
                  AND tc.table_name IN ('incidents', 'resolutions')
                """
            )
            actual_foreign_keys = {
                (table, column, foreign_table, foreign_column)
                for table, column, foreign_table, foreign_column in cursor.fetchall()
            }

            print("\nRELATIONSHIP CHECKS")
            for foreign_key in sorted(REQUIRED_FOREIGN_KEYS):
                table, column, foreign_table, foreign_column = foreign_key
                label = f"{table}.{column} -> {foreign_table}.{foreign_column}"
                checks.append(
                    report(
                        label,
                        foreign_key in actual_foreign_keys,
                        "foreign key exists" if foreign_key in actual_foreign_keys
                        else "foreign key is missing",
                    )
                )

            expected_statuses = {
                "incidents": {"OPEN", "IN_PROGRESS", "RESOLVED", "CLOSED"},
                "resolutions": {
                    "PENDING_REVIEW",
                    "APPROVED",
                    "REJECTED",
                    "CHANGES_REQUESTED",
                },
            }
            cursor.execute(
                """
                SELECT c.conrelid::regclass::text, pg_get_constraintdef(c.oid)
                FROM pg_constraint AS c
                WHERE c.contype = 'c'
                  AND c.connamespace = 'public'::regnamespace
                  AND c.conrelid::regclass::text IN ('incidents', 'resolutions')
                """
            )
            status_check_definitions: dict[str, list[str]] = {}
            for table_name, definition in cursor.fetchall():
                status_check_definitions.setdefault(table_name, []).append(definition)

            for table_name, statuses in expected_statuses.items():
                status_constraint_exists = any(
                    "status" in definition.lower()
                    and all(f"'{status}'" in definition for status in statuses)
                    for definition in status_check_definitions.get(table_name, [])
                )
                checks.append(
                    report(
                        f"{table_name} status constraint",
                        status_constraint_exists,
                        "allowed status values are constrained"
                        if status_constraint_exists
                        else "required status CHECK constraint is missing",
                    )
                )

            if all(table_ready.values()):
                cursor.execute(
                    """
                    SELECT id, role
                    FROM users
                    ORDER BY id
                    """
                )
                users = fetch_dicts(cursor)
                print_records("USERS (id, role)", users)
                checks.append(report("Users readable", True, f"{len(users)} record(s)"))

                cursor.execute(
                    """
                    SELECT id, title, error_code, service, description, status,
                           created_by, created_at, updated_at, resolved_at
                    FROM incidents
                    ORDER BY id
                    """
                )
                incidents = fetch_dicts(cursor)
                print_records("INCIDENTS", incidents)
                checks.append(
                    report("Incidents readable", True, f"{len(incidents)} record(s)")
                )

                cursor.execute(
                    """
                    SELECT id, incident_id, root_cause, resolution_description,
                           steps_taken, additional_notes, submitted_by, status,
                           reviewed_by, review_comment, created_at, reviewed_at
                    FROM resolutions
                    ORDER BY id
                    """
                )
                resolutions = fetch_dicts(cursor)
                print_records("RESOLUTIONS", resolutions)
                checks.append(
                    report(
                        "Resolutions readable",
                        True,
                        f"{len(resolutions)} record(s)",
                    )
                )
                print_records(
                    "REVIEWS (review fields stored on resolutions)",
                    [
                        {
                            "resolution_id": row["id"],
                            "incident_id": row["incident_id"],
                            "status": row["status"],
                            "reviewed_by": row["reviewed_by"],
                            "review_comment": row["review_comment"],
                            "reviewed_at": row["reviewed_at"],
                        }
                        for row in resolutions
                    ],
                )

                cursor.execute(
                    """
                    SELECT
                        (SELECT count(*)
                         FROM resolutions r
                         LEFT JOIN incidents i ON i.id = r.incident_id
                         WHERE i.id IS NULL) AS missing_incidents,
                        (SELECT count(*)
                         FROM incidents i
                         LEFT JOIN users u ON u.id = i.created_by
                         WHERE u.id IS NULL) AS missing_creators,
                        (SELECT count(*)
                         FROM resolutions r
                         LEFT JOIN users u ON u.id = r.submitted_by
                         WHERE u.id IS NULL) AS missing_submitters,
                        (SELECT count(*)
                         FROM resolutions r
                         LEFT JOIN users u ON u.id = r.reviewed_by
                         WHERE r.reviewed_by IS NOT NULL AND u.id IS NULL)
                            AS missing_reviewers,
                        (SELECT count(*)
                         FROM resolutions
                         WHERE reviewed_by IS NULL) AS null_reviewers
                    """
                )
                (
                    missing_incidents,
                    missing_creators,
                    missing_submitters,
                    missing_reviewers,
                    null_reviewers,
                ) = cursor.fetchone()

                for label, count in (
                    ("resolution -> incident", missing_incidents),
                    ("incident -> created_by user", missing_creators),
                    ("resolution -> submitted_by user", missing_submitters),
                    ("resolution -> reviewed_by user when non-NULL", missing_reviewers),
                ):
                    checks.append(
                        report(
                            label,
                            count == 0,
                            "no orphaned references" if count == 0
                            else f"{count} orphaned reference(s)",
                        )
                    )
                checks.append(
                    report(
                        "NULL reviewed_by values",
                        True,
                        f"{null_reviewers} correctly treated as not-yet-attributed",
                    )
                )

                cursor.execute(
                    """
                    SELECT count(*)
                    FROM incidents
                    WHERE status NOT IN ('OPEN', 'IN_PROGRESS', 'RESOLVED', 'CLOSED')
                    """
                )
                invalid_incidents = cursor.fetchone()[0]
                checks.append(
                    report(
                        "Incident status values",
                        invalid_incidents == 0,
                        "all valid" if invalid_incidents == 0
                        else f"{invalid_incidents} invalid value(s)",
                    )
                )

                cursor.execute(
                    """
                    SELECT count(*)
                    FROM resolutions
                    WHERE status NOT IN (
                        'PENDING_REVIEW', 'APPROVED', 'REJECTED', 'CHANGES_REQUESTED'
                    )
                    """
                )
                invalid_resolutions = cursor.fetchone()[0]
                checks.append(
                    report(
                        "Resolution/review status values",
                        invalid_resolutions == 0,
                        "all valid" if invalid_resolutions == 0
                        else f"{invalid_resolutions} invalid value(s)",
                    )
                )

                cursor.execute(
                    """
                    SELECT count(*)
                    FROM incidents
                    WHERE status = 'RESOLVED' AND resolved_at IS NULL
                    """
                )
                missing_resolved_at = cursor.fetchone()[0]
                checks.append(
                    report(
                        "Resolved incidents have resolved_at",
                        missing_resolved_at == 0,
                        "all resolved incidents timestamped"
                        if missing_resolved_at == 0
                        else f"{missing_resolved_at} missing timestamp(s)",
                    )
                )

                cursor.execute(
                    """
                    SELECT count(*)
                    FROM resolutions
                    WHERE status <> 'PENDING_REVIEW' AND reviewed_at IS NULL
                    """
                )
                missing_reviewed_at = cursor.fetchone()[0]
                checks.append(
                    report(
                        "Reviewed resolutions have reviewed_at",
                        missing_reviewed_at == 0,
                        "all reviewed resolutions timestamped"
                        if missing_reviewed_at == 0
                        else f"{missing_reviewed_at} missing timestamp(s)",
                    )
                )
            else:
                for table_name, ready in table_ready.items():
                    if not ready:
                        checks.append(
                            report(
                                f"{table_name} records readable",
                                False,
                                "required columns are missing; query skipped",
                            )
                        )

        connection.rollback()
    except psycopg.Error as error:
        checks.append(
            report("Database verification queries", False, f"{type(error).__name__}: {error}")
        )
    finally:
        connection.close()

    passed = all(checks)
    print(f"\nOVERALL: {'PASS' if passed else 'FAIL'}")
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
