import os
from alembic.config import Config
from alembic import command

def migrate_all():
    """
    Runs Alembic migrations to upgrade the database schema to the latest version.
    This function calculates the project root (two levels up from this file) to locate
    the alembic.ini file, creates an Alembic Config object, and applies all pending migrations.
    
    Note:
    The database URL is dynamically overridden in alembic/env.py using your custom configuration.
    """
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    alembic_ini_path = os.path.join(project_root, "alembic.ini")
    alembic_cfg = Config(alembic_ini_path)
    command.upgrade(alembic_cfg, "head")
    print("Database migration completed successfully.")

