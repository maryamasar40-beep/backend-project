"""add user role

Revision ID: 20260308_0002
Revises: 20260308_0001
Create Date: 2026-03-08 00:20:00
"""

import sqlalchemy as sa

from alembic import op

revision = "20260308_0002"
down_revision = "20260308_0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column("role", sa.String(), nullable=False, server_default="analyst"),
    )


def downgrade() -> None:
    op.drop_column("users", "role")
