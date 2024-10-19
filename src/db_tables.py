from sqlalchemy import (
    MetaData,
    Table,
    Column,
    Integer,
    String,
    Enum,
    ForeignKey,
    PrimaryKeyConstraint,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB, TIMESTAMP, TEXT

metadata_obj = MetaData()
from src import schemas

# Enum definitions
document_type_enum = Enum(schemas.DocumentType, name="document_type")
application_status_enum = Enum(schemas.ApplicationStatus, name="application_status")
organization_role_enum = Enum(schemas.OrganizationRole, name="organization_role")
review_type_enum = Enum(schemas.ReviewType, name="review_type")
gender_enum = Enum(schemas.Gender, name="gender_enum")
organization_type_enum = Enum(schemas.OrganizationType, name="organization_type")
event_status_enum = Enum(schemas.EventStatus, name="event_status")
organization_size = Enum(schemas.OrganizationSize, name="organization_size")

# Table Definitions

users = Table(
    "users",
    metadata_obj,
    Column("id", Integer, primary_key=True),
    Column("email", String, nullable=False, index=True),
    Column("password", String, nullable=True),
    Column("first_name", String, nullable=False),
    Column("last_name", String, nullable=False),
    Column(
        "created_at",
        TIMESTAMP(timezone=True),
        server_default=text("current_timestamp"),
        nullable=False,
    ),
    Column("birth_date", TIMESTAMP(timezone=True), nullable=True),
    Column("avatar", String, nullable=True),
    Column("gender", gender_enum, nullable=False),
)

events = Table(
    "events",
    metadata_obj,
    Column("id", Integer, primary_key=True),
    Column("organizer_id", ForeignKey("organizations.id"), nullable=False, index=True),
    Column("event_name", String, nullable=False),
    Column("location", String, nullable=False),
    Column("description", TEXT, nullable=False),
    Column("phone_contact", String, nullable=False),
    Column("tags", JSONB, nullable=True),
    Column("pictures", JSONB, nullable=True),
    Column("details", JSONB, nullable=True),
    Column("status", event_status_enum, nullable=False, default=text("HIDDEN")),
    Column(
        "start_date",
        TIMESTAMP(timezone=True),
        server_default=text("current_timestamp"),
        nullable=False,
    ),
    Column("duration", Integer, nullable=False),
)

event_applications = Table(
    "event_applications",
    metadata_obj,
    Column("id", Integer, primary_key=True),
    Column("event_id", ForeignKey("events.id"), nullable=False, index=True),
    Column("applicant_id", ForeignKey("organizations.id"), nullable=False, index=True),
    Column("application_data", JSONB, nullable=True),
    Column("status", application_status_enum, nullable=False),
    Column(
        "created_at",
        TIMESTAMP(timezone=True),
        server_default=text("current_timestamp"),
        nullable=False,
    ),
    Column(
        "updated_at",
        TIMESTAMP(timezone=True),
        server_default=text("current_timestamp"),
        nullable=True,
    ),
    Column("updated_by", Integer, nullable=True),
)

documents = Table(
    "documents",
    metadata_obj,
    Column("id", Integer, primary_key=True),
    Column("uploader_id", ForeignKey("organizations.id"), nullable=False, index=True),
    Column("file_url", String, nullable=False),
    Column("name", String, nullable=False),
    Column("type", document_type_enum, nullable=False),
)

application_document = Table(
    "application_document",
    metadata_obj,
    Column("application_id", ForeignKey("event_applications.id"), nullable=False),
    Column("document_id", ForeignKey("documents.id"), nullable=False),
    PrimaryKeyConstraint(
        "application_id", "document_id", name="application_document_pk"
    ),
)

organizations = Table(
    "organizations",
    metadata_obj,
    Column("id", Integer, primary_key=True),
    Column("organization_name", String, nullable=False),
    Column("contact_address", String, nullable=False),
    Column("contact_phone", String, nullable=False),
    Column(
        "organization_type",
        organization_type_enum,
        default=text("VENDOR"),
        nullable=False,
    ),
    Column("email", String, nullable=False),
    Column("size", organization_size, nullable=False),
    Column("years_of_operation", Integer, nullable=False),
)

organization_members = Table(
    "organization_members",
    metadata_obj,
    Column("organization_id", ForeignKey("organizations.id"), nullable=False),
    Column("user_id", ForeignKey("users.id"), nullable=False),
    Column("role", organization_role_enum, nullable=False),
    PrimaryKeyConstraint("organization_id", "user_id", name="organization_members_pk"),
)

organization_rating = Table(
    "organization_rating",
    metadata_obj,
    Column("id", Integer, primary_key=True),
    Column("target_org", ForeignKey("organizations.id"), nullable=False, index=True),
    Column("review", TEXT, nullable=False),
    Column("rating", Integer, nullable=False),
    Column("type", review_type_enum, nullable=False),
    Column("author", ForeignKey("users.id"), nullable=False),
)

user_google_id = Table(
    "user_google_id",
    metadata_obj,
    Column("google_id", String, primary_key=True),
    Column("user_id", ForeignKey("users.id"), nullable=False),
)


countries = Table(
    "countries",
    metadata_obj,
    Column("id", Integer, primary_key=True),
    Column("label", String, nullable=False),
)

cities = Table(
    "cities",
    metadata_obj,
    Column("id", Integer, primary_key=True),
    Column("label", String, nullable=False),
    Column("country", ForeignKey("countries.id"), nullable=False, index=True),
)
