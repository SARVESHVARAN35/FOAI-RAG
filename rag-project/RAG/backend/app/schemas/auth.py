from typing import Literal, TypedDict

from pydantic import BaseModel, ConfigDict, Field, field_validator


UserRole = Literal["SUPPORT_ENGINEER", "IT_LEAD", "ADMIN"]


class CurrentUser(TypedDict):
    id: int
    name: str
    email: str
    role: UserRole


class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    role: UserRole


class LoginRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    email: str = Field(min_length=3, max_length=320)
    password: str = Field(min_length=1, max_length=1024)

    @field_validator("email")
    @classmethod
    def normalize_email(cls, email: str) -> str:
        normalized = email.strip().lower()
        if "@" not in normalized or any(character.isspace() for character in normalized):
            raise ValueError("A valid email address is required.")
        return normalized


class CreateUserRequest(LoginRequest):
    name: str = Field(min_length=1, max_length=200)
    role: UserRole
    password: str = Field(min_length=12, max_length=1024)

    @field_validator("password")
    @classmethod
    def password_fits_bcrypt(cls, password: str) -> str:
        if len(password.encode("utf-8")) > 72:
            raise ValueError("Password must be no longer than 72 UTF-8 bytes.")
        return password

    @field_validator("name")
    @classmethod
    def normalize_name(cls, name: str) -> str:
        normalized = name.strip()
        if not normalized:
            raise ValueError("Name must not be blank.")
        return normalized


class RegisterRequest(LoginRequest):
    name: str = Field(min_length=1, max_length=200)
    role: Literal["SUPPORT_ENGINEER"]
    password: str = Field(min_length=8, max_length=1024)

    @field_validator("password")
    @classmethod
    def password_fits_bcrypt(cls, password: str) -> str:
        if len(password.encode("utf-8")) > 72:
            raise ValueError("Password must be no longer than 72 UTF-8 bytes.")
        return password

    @field_validator("name")
    @classmethod
    def normalize_name(cls, name: str) -> str:
        normalized = name.strip()
        if not normalized:
            raise ValueError("Name must not be blank.")
        return normalized


class TokenResponse(BaseModel):
    access_token: str
    token_type: Literal["bearer"] = "bearer"
    user: UserResponse
