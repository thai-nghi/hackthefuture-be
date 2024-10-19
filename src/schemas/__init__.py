from typing import Any
from pydantic import BaseModel, PositiveInt, validator, EmailStr, root_validator, Field
from datetime import datetime
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

class Gender(enum.Enum):
    MALE = "MALE"
    FEMALE = "FEMALE"
    OTHER = "OTHER"
    UNDISCLOSED = "UNDISCLOSED"

class OrganizationType(enum.Enum):
    EVENT_ORGANIZER = "ORGANIZER"
    VENDOR = "VENDOR"

class EventStatus(enum.Enum):
    HIDDEN = "HIDDEN"
    PUBLIC = "PUBLIC"

class UserBase(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str
    birth_date: datetime
    gender: Gender


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

class GoogleRegister(UserBase):
    google_token: str

class UserLogin(BaseModel):
    email: EmailStr | None
    password: str | None
    google_token: str | None
    
    @root_validator
    def ensure_credentals(cls, values):
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


class UserResponse(UserBase):
    id: int
    organization_id: int | None

class DocumentAttribute(BaseModel):
    file_url: str
    name: str
    type: DocumentType

class Document(DocumentAttribute):
    id: int

class OrganizationAttributes(BaseModel):
    organization_name: str
    contact_address: str
    contact_phone: str
    organization_type: OrganizationType = OrganizationType.VENDOR

class OrganizationIn(OrganizationAttributes):
    documents: list[DocumentAttribute] | None

class Organization(OrganizationAttributes):
    id: int

class Country(BaseModel):
    label: str
    value: int

class City(BaseModel):
    label: str
    value: int
    
class Membership(BaseModel):
    user_id: int
    organization_id: int
    role: OrganizationRole

class PaginationIn(BaseModel):
    currentPage: int = Field(0, ge=0)
    pageSize: int = Field(6, gt=0, lt=100)


class PaginationResponse(PaginationIn):
    total: PositiveInt

class EventListQuery(BaseModel):
    location: str 
    categories: list[str] | str
    page: PaginationIn

class EventListRequest(BaseModel):
    data: EventListQuery

class Tag(BaseModel):
    name: str
    color: str 

class ImageSchema(BaseModel):
    url: str

class EventImage(BaseModel):
    event: list[ImageSchema]
    banner: list[ImageSchema]
    map: ImageSchema

class EventDetailSchema(BaseModel):
    config: str

class EventAttributeIn(BaseModel):
    event_name: str 
    location: str 
    description: str 
    tags: list[Tag] | None    
    phone_contact: str 
    picture: EventImage 
    details: EventDetailSchema 
    status: EventStatus
    start_date: datetime 
    duration: int 

class EventAttributeMid(EventAttributeIn):
    organizer_id: int

class EventAttribute(EventAttributeMid):
    id: int
    organizer: str

class PaginationEventList(BaseModel):
    data: list[EventAttribute] = []
