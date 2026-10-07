import hashlib
import hmac
from datetime import datetime, timedelta, timezone
from typing import Callable

import bcrypt
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.config import settings
from app.db.database import get_connection
from app.schemas.auth import CurrentUser, UserRole


_bearer_scheme = HTTPBearer(auto_error=False)


def hash_password(password: str) -> str:
    return bcrypt.hashpw(
        password.encode("utf-8"),
        bcrypt.gensalt(),
    ).decode("ascii")


def verify_password(password: str, stored_hash: str) -> bool:
    if stored_hash.startswith("pbkdf2_sha256$"):
        return _verify_legacy_pbkdf2_password(password, stored_hash)

    try:
        password_bytes = password.encode("utf-8")
        if len(password_bytes) > 72:
            return False
        return bcrypt.checkpw(password_bytes, stored_hash.encode("ascii"))
    except (UnicodeEncodeError, ValueError, TypeError):
        return False


def _verify_legacy_pbkdf2_password(password: str, stored_hash: str) -> bool:
    try:
        algorithm, iterations_text, salt, expected_hash = stored_hash.split("$")
        iterations = int(iterations_text)
        if (
            algorithm != "pbkdf2_sha256"
            or not 1_000 <= iterations <= 2_000_000
            or len(expected_hash) != 64
        ):
            return False
        int(expected_hash, 16)
        expected_hash_bytes = expected_hash.lower().encode("ascii")
        actual_hash = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt.encode("ascii"),
            iterations,
        ).hex().encode("ascii")
        return hmac.compare_digest(actual_hash, expected_hash_bytes)
    except (UnicodeEncodeError, ValueError):
        return False


def create_access_token(user: CurrentUser) -> str:
    issued_at = datetime.now(timezone.utc)
    expires_at = issued_at + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    payload = {
        "sub": str(user["id"]),
        "user_id": user["id"],
        "email": user["email"],
        "role": user["role"],
        "iat": issued_at,
        "exp": expires_at,
    }
    return jwt.encode(
        payload,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer_scheme),
) -> CurrentUser:
    unauthorized = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or missing authentication credentials.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if credentials is None:
        raise unauthorized

    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
            options={
                "require": [
                    "sub",
                    "user_id",
                    "email",
                    "role",
                    "iat",
                    "exp",
                ]
            },
        )
    except jwt.InvalidTokenError:
        raise unauthorized from None

    user_id = payload.get("user_id")
    if (
        not isinstance(user_id, int)
        or isinstance(user_id, bool)
        or payload.get("sub") != str(user_id)
    ):
        raise unauthorized

    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT id, name, email, role
                FROM users
                WHERE id = %s
                """,
                (user_id,),
            )
            row = cursor.fetchone()
    finally:
        connection.close()

    if row is None:
        raise unauthorized

    return {
        "id": row[0],
        "name": row[1],
        "email": row[2],
        "role": row[3],
    }


def require_roles(*allowed_roles: UserRole) -> Callable[..., CurrentUser]:
    def role_dependency(
        current_user: CurrentUser = Depends(get_current_user),
    ) -> CurrentUser:
        if current_user["role"] not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to perform this action.",
            )
        return current_user

    return role_dependency
