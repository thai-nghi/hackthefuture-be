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
    PAYMENT_REQUEST = "PAYMENT_REQUEST"
    FINALIZED = "FINALIZED"


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


class OrganizationSize(enum.Enum):
    LARGE = "LARGE"
    MEDIUM = "MEDIUM"
    SMALL = "SMALL"


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

class Tag(BaseModel):
    value: int
    label: str

class UserResponse(UserBase):
    id: int
    organization_id: int | None
    avatar: str | None


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
    years_of_operation: int
    size: OrganizationSize
    email: str
    organization_type: OrganizationType = OrganizationType.VENDOR
    country: int
    city: int

class OrganizationIn(OrganizationAttributes):
    documents: list[DocumentAttribute] | None
    tags: list[int] | None
    
class Organization(OrganizationAttributes):
    id: int
    tags: list[Tag] | None
    country_label: str
    city_label: str

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


class ImageSchema(BaseModel):
    url: str


class EventImage(BaseModel):
    event: list[ImageSchema]
    banner: list[ImageSchema]
    map: ImageSchema


class EventDetailSchema(BaseModel):
    config: dict[str, Any]


class EventAttributeIn(BaseModel):
    event_name: str
    street_addr: str
    description: str
    tags: list[int] | None
    phone_contact: str
    pictures: EventImage
    details: EventDetailSchema
    status: EventStatus = EventStatus.HIDDEN
    start_date: datetime
    end_date: datetime
    city: int
    country: int


class EventAttributeMid(EventAttributeIn):
    organizer_id: int


class EventAttribute(EventAttributeMid):
    id: int
    organizer: str
    city: str
    country: str
    tags: list[Tag] | None


class PaginationEventList(BaseModel):
    data: list[EventAttribute] = []

class EventApplicationIn(BaseModel):
    application_data: dict[str, Any]
    

class EventApplicationMid(EventApplicationIn):
    event_id: int
    created_at: datetime
    updated_at: datetime
    updated_by: int
    status: ApplicationStatus

class EventApplication(EventApplicationMid):
    id: int
    applicant_name: str
    applicant_address: str
    applicant_phone: str
    applicant_email: str
    applicant_size: OrganizationSize
    applicant_years_of_operation: int
    applicant_country: int
    applicant_city: int
    applicant_country_label: str
    applicant_city_label: str
    event_name: str

class ApplicationStatusIn(BaseModel):
    status: ApplicationStatus
