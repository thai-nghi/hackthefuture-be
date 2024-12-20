"""empty message

Revision ID: 91a7f91e22b8
Revises: d694553f938e
Create Date: 2024-10-21 11:31:31.265749

"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "91a7f91e22b8"
down_revision = "d694553f938e"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column("events", sa.Column("street_addr", sa.String(), nullable=False))
    op.add_column(
        "events",
        sa.Column(
            "end_date",
            postgresql.TIMESTAMP(timezone=True),
            server_default=sa.text("current_timestamp"),
            nullable=False,
        ),
    )
    op.add_column("events", sa.Column("country", sa.Integer(), nullable=False))
    op.add_column("events", sa.Column("city", sa.Integer(), nullable=False))
    op.create_index(op.f("ix_events_city"), "events", ["city"], unique=False)
    op.create_index(op.f("ix_events_country"), "events", ["country"], unique=False)
    op.create_foreign_key(None, "events", "countries", ["country"], ["id"])
    op.create_foreign_key(None, "events", "cities", ["city"], ["id"])
    op.drop_column("events", "location")
    op.add_column("organizations", sa.Column("country", sa.Integer(), nullable=False))
    op.add_column("organizations", sa.Column("city", sa.Integer(), nullable=False))
    op.create_index(
        op.f("ix_organizations_city"), "organizations", ["city"], unique=False
    )
    op.create_index(
        op.f("ix_organizations_country"), "organizations", ["country"], unique=False
    )
    op.create_foreign_key(None, "organizations", "countries", ["country"], ["id"])
    op.create_foreign_key(None, "organizations", "cities", ["city"], ["id"])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, "organizations", type_="foreignkey")
    op.drop_constraint(None, "organizations", type_="foreignkey")
    op.drop_index(op.f("ix_organizations_country"), table_name="organizations")
    op.drop_index(op.f("ix_organizations_city"), table_name="organizations")
    op.drop_column("organizations", "city")
    op.drop_column("organizations", "country")
    op.add_column(
        "events",
        sa.Column("location", sa.VARCHAR(), autoincrement=False, nullable=False),
    )
    op.drop_constraint(None, "events", type_="foreignkey")
    op.drop_constraint(None, "events", type_="foreignkey")
    op.drop_index(op.f("ix_events_country"), table_name="events")
    op.drop_index(op.f("ix_events_city"), table_name="events")
    op.drop_column("events", "city")
    op.drop_column("events", "country")
    op.drop_column("events", "end_date")
    op.drop_column("events", "street_addr")
    # ### end Alembic commands ###
