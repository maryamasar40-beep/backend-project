"""initial schema

Revision ID: 20260308_0001
Revises:
Create Date: 2026-03-08 00:00:00
"""

import sqlalchemy as sa

from alembic import op

revision = "20260308_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "brands",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("domains", sa.JSON(), nullable=False),
        sa.Column("logo_embeddings", sa.JSON(), nullable=True),
        sa.Column("colors_json", sa.JSON(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )
    op.create_index(op.f("ix_brands_id"), "brands", ["id"], unique=False)

    op.create_table(
        "scans",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("url", sa.String(), nullable=False),
        sa.Column("domain", sa.String(), nullable=False),
        sa.Column("screenshot_hash", sa.String(), nullable=True),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_scans_id"), "scans", ["id"], unique=False)

    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("email", sa.String(), nullable=False),
        sa.Column("hashed_password", sa.String(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)
    op.create_index(op.f("ix_users_id"), "users", ["id"], unique=False)

    op.create_table(
        "whitelist",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("domain", sa.String(), nullable=False),
        sa.Column(
            "verified_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column("logo_hash", sa.String(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("domain", name="uq_whitelist_domain"),
    )
    op.create_index(op.f("ix_whitelist_domain"), "whitelist", ["domain"], unique=False)
    op.create_index(op.f("ix_whitelist_id"), "whitelist", ["id"], unique=False)

    op.create_table(
        "results",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("scan_id", sa.Integer(), nullable=False),
        sa.Column("risk_score", sa.Float(), nullable=False),
        sa.Column("classification", sa.String(), nullable=False),
        sa.Column("details_json", sa.JSON(), nullable=True),
        sa.Column("model_version", sa.String(), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.ForeignKeyConstraint(["scan_id"], ["scans.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_results_id"), "results", ["id"], unique=False)
    op.create_index(op.f("ix_results_scan_id"), "results", ["scan_id"], unique=False)

    op.create_table(
        "feedback",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("result_id", sa.Integer(), nullable=False),
        sa.Column("user_verdict", sa.String(), nullable=False),
        sa.Column("comment", sa.String(), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.ForeignKeyConstraint(["result_id"], ["results.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_feedback_id"), "feedback", ["id"], unique=False)
    op.create_index(op.f("ix_feedback_result_id"), "feedback", ["result_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_feedback_result_id"), table_name="feedback")
    op.drop_index(op.f("ix_feedback_id"), table_name="feedback")
    op.drop_table("feedback")

    op.drop_index(op.f("ix_results_scan_id"), table_name="results")
    op.drop_index(op.f("ix_results_id"), table_name="results")
    op.drop_table("results")

    op.drop_index(op.f("ix_whitelist_id"), table_name="whitelist")
    op.drop_index(op.f("ix_whitelist_domain"), table_name="whitelist")
    op.drop_table("whitelist")

    op.drop_index(op.f("ix_users_id"), table_name="users")
    op.drop_index(op.f("ix_users_email"), table_name="users")
    op.drop_table("users")

    op.drop_index(op.f("ix_scans_id"), table_name="scans")
    op.drop_table("scans")

    op.drop_index(op.f("ix_brands_id"), table_name="brands")
    op.drop_table("brands")
