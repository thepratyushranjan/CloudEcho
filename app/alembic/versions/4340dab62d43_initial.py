from alembic import op
import sqlalchemy as sa
from sqlalchemy.engine.reflection import Inspector
from pgvector.sqlalchemy import Vector

# revision identifiers, used by Alembic.
revision = '4340dab62d43'
down_revision = None
branch_labels = None
depends_on = None

def table_exists(table_name, conn):
    """Check if a table exists in the database."""
    inspector = Inspector.from_engine(conn)
    return table_name in inspector.get_table_names()

def upgrade():
    conn = op.get_bind()
    # Ensure the uuid-ossp extension is available for UUID generation.
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp";')

    # Ensure the pgvector extension is available for vector operations.
    op.execute('CREATE EXTENSION IF NOT EXISTS "vector";')

    # Create the 'document_chunks' table if it doesn't exist.
    if not table_exists('document_chunks', conn):
        op.create_table(
            'document_chunks',
            sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column('content', sa.Text(), nullable=False),
            sa.Column('embedding', Vector(1536), nullable=False),
        )
        print("Table 'document_chunks' created.")
    else:
        print("Table 'document_chunks' already exists.")

    # Create the 'langchain_pg_collection' table if it doesn't exist.
    if not table_exists('langchain_pg_collection', conn):
        op.create_table(
            'langchain_pg_collection',
            sa.Column(
                'uuid',
                sa.dialects.postgresql.UUID(as_uuid=True),
                primary_key=True,
                server_default=sa.text('uuid_generate_v4()')
            ),
            sa.Column('name', sa.String(), nullable=False),
            sa.Column('cmetadata', sa.JSON(), nullable=True),
        )
        print("Table 'langchain_pg_collection' created.")
    else:
        print("Table 'langchain_pg_collection' already exists.")

    # Create the 'langchain_pg_embedding' table if it doesn't exist.
    if not table_exists('langchain_pg_embedding', conn):
        op.create_table(
            'langchain_pg_embedding',
            sa.Column(
                'id', 
                sa.String(), 
                primary_key=True, 
                server_default=sa.text("uuid_generate_v4()")
            ),
            sa.Column(
                'collection_id',
                sa.dialects.postgresql.UUID(as_uuid=True),
                sa.ForeignKey("langchain_pg_collection.uuid"),
                nullable=False
            ),
            sa.Column('embedding', Vector(), nullable=False),
            sa.Column('document', sa.String(), nullable=False),
            sa.Column('cmetadata', sa.dialects.postgresql.JSONB(), nullable=True),
        )
        print("Table 'langchain_pg_embedding' created.")
    else:
        print("Table 'langchain_pg_embedding' already exists.")

def downgrade():
    op.drop_table('langchain_pg_embedding')
    op.drop_table('langchain_pg_collection')
    op.drop_table('document_chunks')
    
    # Drop extensions (order matters - drop vector before uuid-ossp)
    op.execute('DROP EXTENSION IF EXISTS "vector";')
    op.execute('DROP EXTENSION IF EXISTS "uuid-ossp";')
