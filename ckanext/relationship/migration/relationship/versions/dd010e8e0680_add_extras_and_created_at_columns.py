"""Add extras and created_at columns.

Revision ID: dd010e8e0680
Revises: aca2ff1d3ce4
Create Date: 2024-10-31 01:30:49.251175

"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB

# revision identifiers, used by Alembic.
revision = "dd010e8e0680"
down_revision = "aca2ff1d3ce4"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "relationship_relationship",
        sa.Column("extras", JSONB, nullable=False, server_default="{}"),
    )
    op.add_column(
        "relationship_relationship",
        sa.Column(
            "created_at", sa.DateTime, nullable=False, server_default=sa.text("now()")
        ),
    )


def downgrade():
    op.drop_column("relationship_relationship", "created_at")
    op.drop_column("relationship_relationship", "extras")
