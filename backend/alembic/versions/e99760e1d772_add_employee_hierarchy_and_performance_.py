"""Add employee hierarchy and performance reviews

Revision ID: e99760e1d772
Revises: c698633f429e
Create Date: 2026-02-02 20:19:39.129233

"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql
from sqlalchemy.engine.reflection import Inspector

# revision identifiers, used by Alembic.
revision = "e99760e1d772"
down_revision = 'c698633f429e'
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()
    inspector = Inspector.from_engine(conn)
    existing_tables = inspector.get_table_names()

    # Create performance_reviews if not exists
    if 'performance_reviews' not in existing_tables:
        op.create_table('performance_reviews',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('employee_id', sa.Integer(), nullable=False),
            sa.Column('manager_id', sa.Integer(), nullable=False),
            sa.Column('quarter', sa.Integer(), nullable=False),
            sa.Column('year', sa.Integer(), nullable=False),
            sa.Column('rating', sa.Float(), nullable=True),
            sa.Column('feedback', sa.Text(), nullable=True),
            sa.Column('ai_insights', sa.JSON(), nullable=True),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
            sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
            sa.ForeignKeyConstraint(['employee_id'], ['employees.id'], ),
            sa.ForeignKeyConstraint(['manager_id'], ['employees.id'], ),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index(op.f('ix_performance_reviews_id'), 'performance_reviews', ['id'], unique=False)

    # Handle employee_metrics index
    existing_indices_metrics = [idx['name'] for idx in inspector.get_indexes('employee_metrics')]
    if 'ix_employee_metrics_id' not in existing_indices_metrics:
        op.create_index(op.f('ix_employee_metrics_id'), 'employee_metrics', ['id'], unique=False)

    # Handle employees columns
    existing_columns_employees = [col['name'] for col in inspector.get_columns('employees')]
    if 'job_title' not in existing_columns_employees:
        op.add_column('employees', sa.Column('job_title', sa.String(length=100), nullable=True))
    if 'manager_id' not in existing_columns_employees:
        op.add_column('employees', sa.Column('manager_id', sa.Integer(), nullable=True))
    if 'position_level' not in existing_columns_employees:
        op.add_column('employees', sa.Column('position_level', sa.String(length=50), nullable=True))

    # Handle employee indices
    existing_indices_employees = [idx['name'] for idx in inspector.get_indexes('employees')]
    if 'ix_employees_email' not in existing_indices_employees:
        op.create_index(op.f('ix_employees_email'), 'employees', ['email'], unique=False)
    if 'ix_employees_id' not in existing_indices_employees:
        op.create_index(op.f('ix_employees_id'), 'employees', ['id'], unique=False)
    if 'ix_employees_run_month' not in existing_indices_employees:
        op.create_index(op.f('ix_employees_run_month'), 'employees', ['run_month'], unique=False)
    
    # Handle unique constraint
    # op.create_unique_constraint('uq_employee_run_month_email', 'employees', ['run_month', 'email'])
    
    # Handle foreign key
    existing_fks = inspector.get_foreign_keys('employees')
    if not any(fk['constrained_columns'] == ['manager_id'] for fk in existing_fks):
        op.create_foreign_key('fk_employee_manager', 'employees', 'employees', ['manager_id'], ['id'])


def downgrade():
    pass # Keep it simple for now as we are in fix mode
