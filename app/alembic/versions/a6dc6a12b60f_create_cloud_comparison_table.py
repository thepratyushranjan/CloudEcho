"""create cloud_comparison table

Revision ID: a6dc6a12b60f
Revises: 4340dab62d43
Create Date: 2025-05-07 10:56:50.928590

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.engine.reflection import Inspector

# revision identifiers, used by Alembic.
revision = 'a6dc6a12b60f'
down_revision = '4340dab62d43'
branch_labels = None
depends_on = None

def table_exists(table_name: str, conn) -> bool:
    """Check if a table exists in the database."""
    inspector = Inspector.from_engine(conn)
    return table_name in inspector.get_table_names()

def upgrade() -> None:
    conn = op.get_bind()

    # Create 'cloud_comparison' if it doesn't exist
    if not table_exists('cloud_comparison', conn):
        op.create_table(
            'cloud_comparison',
            sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column('region', sa.String(), nullable=False),
            sa.Column('location', sa.String(), nullable=False),
            sa.Column('instance_type', sa.String(), nullable=False),
            sa.Column('instance_family', sa.String(), nullable=False),
            sa.Column('vcpus', sa.Integer(), nullable=False),
            sa.Column('ram_gib', sa.Float(), nullable=False),
            sa.Column('memory_mib', sa.Integer(), nullable=False),
            sa.Column('cost_per_hour', sa.Float(), nullable=True),
            sa.Column(
                'cloud',
                sa.Enum('AWS', 'Azure', 'GCP', name='cloud_enum'),
                nullable=False
            ),
        )
        print("Table 'cloud_comparison' created.")
    else:
        print("Table 'cloud_comparison' already exists; skipping creation.")

def downgrade() -> None:
    conn = op.get_bind()

    # Drop 'cloud_comparison' if it exists
    if table_exists('cloud_comparison', conn):
        op.drop_table('cloud_comparison')
        print("Table 'cloud_comparison' dropped.")
    else:
        print("Table 'cloud_comparison' does not exist; skipping drop.")
