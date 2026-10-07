import psycopg
from fastapi import APIRouter, Depends, HTTPException, status

from app.core.security import (
    create_access_token,
    get_current_user,
    hash_password,
    require_roles,
    verify_password,
)
from app.db.database import get_connection
from app.schemas.auth import (
    CreateUserRequest,
    CurrentUser,
    LoginRequest,
    RegisterRequest,
    TokenResponse,
    UserResponse,
)


router = APIRouter(prefix="/auth", tags=["Authentication"])


def _insert_user(request: CreateUserRequest | RegisterRequest) -> dict:
    password_hash = hash_password(request.password)
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT 1 FROM users WHERE lower(email) = %s",
                (request.email,),
            )
            if cursor.fetchone() is not None:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="A user with this email already exists.",
                )

            try:
                cursor.execute(
                    """
                    INSERT INTO users (name, email, password_hash, role)
                    VALUES (%s, %s, %s, %s)
                    RETURNING id, name, email, role
                    """,
                    (
                        request.name,
                        request.email,
                        password_hash,
                        request.role,
                    ),
                )
            except psycopg.errors.UniqueViolation:
                connection.rollback()
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="A user with this email already exists.",
                ) from None
            row = cursor.fetchone()
        connection.commit()
    finally:
        connection.close()

    return {
        "id": row[0],
        "name": row[1],
        "email": row[2],
        "role": row[3],
    }


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(request: RegisterRequest):
    return _insert_user(request)


@router.post("/login", response_model=TokenResponse)
def login(credentials: LoginRequest):
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT id, name, email, role, password_hash
                FROM users
                WHERE lower(email) = %s
                """,
                (credentials.email,),
            )
            row = cursor.fetchone()
    finally:
        connection.close()

    if row is None or not verify_password(credentials.password, row[4]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user: CurrentUser = {
        "id": row[0],
        "name": row[1],
        "email": row[2],
        "role": row[3],
    }
    return {
        "access_token": create_access_token(user),
        "token_type": "bearer",
        "user": user,
    }


@router.get("/me", response_model=UserResponse)
def read_current_user(
    current_user: CurrentUser = Depends(get_current_user),
):
    return current_user


@router.get("/users", response_model=list[UserResponse])
def list_users(
    _admin: CurrentUser = Depends(require_roles("ADMIN")),
):
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT id, name, email, role
                FROM users
                ORDER BY id
                """
            )
            rows = cursor.fetchall()
    finally:
        connection.close()

    return [
        {"id": row[0], "name": row[1], "email": row[2], "role": row[3]}
        for row in rows
    ]


@router.post(
    "/users",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_user(
    request: CreateUserRequest,
    _admin: CurrentUser = Depends(require_roles("ADMIN")),
):
    return _insert_user(request)
