"""${message}

Revision ID: ${up_revision}
Revises: ${down_revision | comma,n}
Create Date: ${create_date}

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.engine.reflection import Inspector
${imports if imports else ""}

# revision identifiers, used by Alembic.
revision: str = ${repr(up_revision)}
down_revision: Union[str, None] = ${repr(down_revision)}
branch_labels: Union[str, Sequence[str], None] = ${repr(branch_labels)}
depends_on: Union[str, Sequence[str], None] = ${repr(depends_on)}

def table_exists(table_name: str, conn) -> bool:
    """Check if a table exists in the database."""
    inspector = Inspector.from_engine(conn)
    return table_name in inspector.get_table_names()

def column_exists(table_name: str, column_name: str, conn) -> bool:
    """Check if a column exists in a table."""
    inspector = Inspector.from_engine(conn)
    try:
        columns = inspector.get_columns(table_name)
        return any(col['name'] == column_name for col in columns)
    except Exception:
        return False

def upgrade() -> None:
    """Upgrade schema."""
    conn = op.get_bind()
    ${upgrades if upgrades else "pass"}

def downgrade() -> None:
    """Downgrade schema."""
    ${downgrades if downgrades else "pass"}