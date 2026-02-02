"""add employee_metrics table

Revision ID: c698633f429e
Revises: c69f8c2d4085
Create Date: 2026-01-24 01:02:34.190288
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "c698633f429e"
down_revision = 'c69f8c2d4085'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "employee_metrics",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("employee_id", sa.Integer(), nullable=False),
        sa.Column("run_month", sa.String(length=7), nullable=False),

        sa.Column("hourly_rate", sa.Float(), nullable=False),
        sa.Column("dept_avg_hourly", sa.Float(), nullable=False),

        sa.Column("peer_percentile", sa.Float(), nullable=False),
        sa.Column("efficiency_score", sa.Float(), nullable=False),

        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),

        sa.UniqueConstraint(
            "employee_id", "run_month", name="uq_employee_run"
        ),

        sa.ForeignKeyConstraint(
            ["employee_id"],
            ["employees.id"],
            ondelete="CASCADE",
            name="fk_metrics_employee",
        ),
    )


def downgrade():
    op.drop_table("employee_metrics")
