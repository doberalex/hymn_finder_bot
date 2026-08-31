#!/bin/bash
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
BACKUP_DIR="$PROJECT_DIR/backups"

set -a
# shellcheck disable=SC1091
source "$PROJECT_DIR/.env"
set +a

mkdir -p "$BACKUP_DIR"
BACKUP_FILE="$BACKUP_DIR/hymn_finder_$(date +%Y%m%d_%H%M%S).sql.gz"

MYSQL_PWD="$DB_PASSWORD" mysqldump \
    --host="$DB_HOST" \
    --port="$DB_PORT" \
    --user="$DB_USER" \
    --single-transaction \
    --quick \
    "$DB_NAME" | gzip > "$BACKUP_FILE"

chmod 600 "$BACKUP_FILE"
echo "$BACKUP_FILE"
