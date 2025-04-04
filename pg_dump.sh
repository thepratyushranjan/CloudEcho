#!/bin/bash

# === Configuration ===
CONTAINER_NAME="pg-vector-db"
DB_USER="postgres"
DB_NAME="app"
DUMP_FILE_NAME="pgvector_backup_$(date +%Y%m%d_%H%M%S).dump"
LOCAL_BACKUP_PATH="./$DUMP_FILE_NAME"
TMP_CONTAINER_PATH="/tmp/$DUMP_FILE_NAME"

# === Backup Function ===
backup_pgvector() {
    echo "[INFO] Backing up PostgreSQL DB from Docker container..."

    # Run pg_dump inside container and export
    docker exec -t $CONTAINER_NAME pg_dump -U $DB_USER -d $DB_NAME -F c -f $TMP_CONTAINER_PATH

    # Copy dump file from container to host
    docker cp $CONTAINER_NAME:$TMP_CONTAINER_PATH $LOCAL_BACKUP_PATH

    echo "[SUCCESS] Backup created: $LOCAL_BACKUP_PATH"
}

# === Restore Function ===
restore_pgvector() {
    if [ -z "$1" ]; then
        echo "[ERROR] Please provide the path to the dump file."
        echo "Usage: $0 restore /path/to/your_dump_file.dump"
        exit 1
    fi

    RESTORE_FILE=$1
    RESTORE_DB_NAME=${2:-restored_pgvector_db}

    echo "[INFO] Copying dump file into Docker container..."
    docker cp "$RESTORE_FILE" $CONTAINER_NAME:/tmp/restore_file.dump

    echo "[INFO] Creating database '$RESTORE_DB_NAME' (if not exists)..."
    docker exec -i $CONTAINER_NAME psql -U $DB_USER -c "CREATE DATABASE $RESTORE_DB_NAME;"

    echo "[INFO] Restoring database from dump..."
    docker exec -i $CONTAINER_NAME pg_restore -U $DB_USER -d $RESTORE_DB_NAME /tmp/restore_file.dump

    echo "[SUCCESS] Restore completed into database: $RESTORE_DB_NAME"
}

# === Main ===
case "$1" in
    backup)
        backup_pgvector
        ;;
    restore)
        restore_pgvector "$2" "$3"
        ;;
    *)
        echo "Usage:"
        echo "  $0 backup                    - Create a backup from the running container"
        echo "  $0 restore <file> [new_db]  - Restore a backup into a new database"
        ;;
esac
