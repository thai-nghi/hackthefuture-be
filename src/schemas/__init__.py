from typing import Any
from datetime import datetime
from pydantic import BaseModel, validator, EmailStr, root_validator
import enum

class DocumentType(enum.Enum):
    APPLICATION = "APPLICATION"
    ORGANIZATION = "ORGANIZATION"

class ApplicationStatus(enum.Enum):
    IN_PROGRESS = "IN_PROGRESS"
    APPROVE = "APPROVE"
    REJECTED = "REJECTED"

class OrganizationRole(enum.Enum):
    ADMIN = "ADMIN"
    STAFF = "STAFF"

class ReviewType(enum.Enum):
    EVENT = "EVENT"
    VENDOR = "VENDOR"


class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    city: str
    country: str


class UserCreate(UserBase):
    password: str | None


class GoogleCredentalData(BaseModel):
    sub: str
    email: str
    given_name: str
    family_name: str
    picture: str


class UserRegister(UserBase):
    password: str
    confirm_password: str

    @validator("confirm_password")
    def verify_password_match(cls, v, values, **kwargs):
        password = values.get("password")

        if v != password:
            raise ValueError("The two passwords did not match.")

        return v


class UserLogin(BaseModel):
    email: EmailStr | None
    password: str | None
    google_token: str | None
    
    @root_validator
    def ensure_credentals(cls, values):
        print(values)
        if "username" in values:
            values["email"] = values["username"]
        if "email" not in values and "google_token" not in values:
            raise ValueError("Either email or google_token is needed")
        if "email" in values and "password" not in values:
            raise ValueError("Password is required for login with email")

        return values

class JwtTokenSchema(BaseModel):
    token: str
    payload: dict
    expire: datetime


class TokenPair(BaseModel):
    access: JwtTokenSchema
    refresh: JwtTokenSchema


class SuccessResponseScheme(BaseModel):
    msg: str
