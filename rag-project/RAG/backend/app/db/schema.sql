BEGIN;

-- Stop safely if the existing users table has a different structure.
DO $$
DECLARE
    missing_columns TEXT[];
BEGIN
    IF to_regclass('public.users') IS NOT NULL THEN
        SELECT array_agg(required.column_name ORDER BY required.column_name)
        INTO missing_columns
        FROM unnest(ARRAY[
            'name',
            'email',
            'password_hash',
            'role',
            'created_at',
            'updated_at'
        ]) AS required(column_name)
        WHERE NOT EXISTS (
            SELECT 1
            FROM information_schema.columns AS existing
            WHERE existing.table_schema = 'public'
              AND existing.table_name = 'users'
              AND existing.column_name = required.column_name
        );

        IF missing_columns IS NOT NULL THEN
            RAISE EXCEPTION
                'Existing public.users table is missing required columns: %. No tables were created.',
                array_to_string(missing_columns, ', ');
        END IF;
    END IF;
END;
$$;

CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL CHECK (role IN ('SUPPORT_ENGINEER', 'IT_LEAD', 'ADMIN')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS incidents (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    error_code TEXT,
    service TEXT,
    description TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'OPEN'
        CHECK (status IN ('OPEN', 'IN_PROGRESS', 'RESOLVED', 'CLOSED')),
    created_by INTEGER NOT NULL REFERENCES users(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS incident_attachments (
    id SERIAL PRIMARY KEY,
    incident_id INTEGER NOT NULL REFERENCES incidents(id),
    filename TEXT NOT NULL,
    file_path TEXT NOT NULL,
    file_type TEXT NOT NULL,
    uploaded_by INTEGER NOT NULL REFERENCES users(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS resolutions (
    id SERIAL PRIMARY KEY,
    incident_id INTEGER NOT NULL REFERENCES incidents(id),
    root_cause TEXT NOT NULL,
    resolution_description TEXT NOT NULL,
    steps_taken TEXT,
    additional_notes TEXT,
    submitted_by INTEGER NOT NULL REFERENCES users(id),
    status TEXT NOT NULL DEFAULT 'PENDING_REVIEW'
        CHECK (status IN ('PENDING_REVIEW', 'APPROVED', 'REJECTED', 'CHANGES_REQUESTED')),
    reviewed_by INTEGER REFERENCES users(id),
    review_comment TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    reviewed_at TIMESTAMPTZ,
    approved_at TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS reviews (
    id SERIAL PRIMARY KEY,
    resolution_id INTEGER NOT NULL REFERENCES resolutions(id),
    reviewer_id INTEGER NOT NULL REFERENCES users(id),
    decision TEXT NOT NULL,
    comment TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS knowledge_documents (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    document_type TEXT NOT NULL CHECK (
        document_type IN (
            'RUNBOOK',
            'POSTMORTEM',
            'INCIDENT_REPORT',
            'TROUBLESHOOTING_GUIDE',
            'TECHNICAL_DOCUMENTATION',
            'APPROVED_RESOLUTION'
        )
    ),
    description TEXT,
    file_path TEXT NOT NULL,
    uploaded_by INTEGER NOT NULL REFERENCES users(id),
    status TEXT NOT NULL DEFAULT 'PENDING_REVIEW'
        CHECK (status IN ('APPROVED', 'PENDING_REVIEW', 'REJECTED', 'OUTDATED')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

COMMIT;