from sqlalchemy import (
    MetaData,
    Table,
    Column,
    Integer,
    String,
    Enum,
    ForeignKey,
    PrimaryKeyConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB, TIMESTAMP, TEXT

metadata_obj = MetaData()
from src import schemas

# Enum definitions
document_type_enum = Enum(schemas.DocumentType, name='document_type')
application_status_enum = Enum(schemas.ApplicationStatus, name='application_status')
organization_role_enum = Enum(schemas.OrganizationRole, name='organization_role')
review_type_enum = Enum(schemas.ReviewType, name='review_type')

# Table Definitions

users = Table(
    "users",
    metadata_obj,
    Column("id", Integer, primary_key=True),
    Column("email", String, nullable=False),
    Column("password", String, nullable=False),
    Column("first_name", String, nullable=False),
    Column("last_name", String, nullable=False),
    Column("created_at", TIMESTAMP, nullable=False),
    Column("age", Integer, nullable=True),
    Column("avatar", String, nullable=True),
)

events = Table(
    "events",
    metadata_obj,
    Column("id", Integer, primary_key=True),
    Column("organizer_id", ForeignKey("organizations.id"), nullable=False),
    Column("event_name", String, nullable=False),
    Column("location", String, nullable=False),
    Column("description", TEXT, nullable=False),
    Column("phone_contact", String, nullable=False),
    Column("pictures", JSONB, nullable=True),
    Column("details", JSONB, nullable=True),
    Column("start_date", TIMESTAMP, nullable=False),
    Column("duration", Integer, nullable=False),
)

event_applications = Table(
    "event_applications",
    metadata_obj,
    Column("id", Integer, primary_key=True),
    Column("event_id", ForeignKey("events.id"), nullable=False),
    Column("applicant_id", ForeignKey("organizations.id"), nullable=False),
    Column("application_data", JSONB, nullable=True),
    Column("status", application_status_enum, nullable=False),
    Column("created_at", TIMESTAMP, nullable=False),
    Column("updated_at", TIMESTAMP, nullable=True),
    Column("updated_by", Integer, nullable=True),
)

documents = Table(
    "documents",
    metadata_obj,
    Column("id", Integer, primary_key=True),
    Column("uploader_id", ForeignKey("organizations.id"), nullable=False),
    Column("file_url", String, nullable=False),
    Column("name", String, nullable=False),
    Column("type",document_type_enum, nullable=False),
)

application_document = Table(
    "application_document",
    metadata_obj,
    Column("application_id", ForeignKey("event_applications.id"), nullable=False),
    Column("document_id", ForeignKey("documents.id"), nullable=False),
    PrimaryKeyConstraint("application_id", "document_id", name="application_document_pk"),
)

organizations = Table(
    "organizations",
    metadata_obj,
    Column("id", Integer, primary_key=True),
    Column("organization_name", String, nullable=False),
    Column("contact_address", String, nullable=False),
    Column("contact_phone", String, nullable=False),
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
    Column("target_org", ForeignKey("organizations.id"), nullable=False),
    Column("review", TEXT, nullable=False),
    Column("rating", Integer, nullable=False),
    Column("type", review_type_enum, nullable=False),
    Column("author", ForeignKey("users.id"), nullable=False),
)