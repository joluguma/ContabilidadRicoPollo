#!/usr/bin/env bash
# Respaldo de ERP Colombia: base de datos (pg_dump) + filestore adjuntos.
# Uso: ./scripts/backup.sh [nombre_base_de_datos]
set -euo pipefail
cd "$(dirname "$0")/.."

DB_NAME="${1:-odoo19}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="backups/${TIMESTAMP}"
mkdir -p "$BACKUP_DIR"

echo "Respaldando base de datos '$DB_NAME'..."
echo "(si pide contraseña: es la de db_password en odoo.conf, o exporta ODOO_DB_PASSWORD antes)"
if [ -n "${ODOO_DB_PASSWORD:-}" ]; then
  export PGPASSWORD="$ODOO_DB_PASSWORD"
fi
/Library/PostgreSQL/18/bin/pg_dump \
  -U odoo -h localhost -Fc "$DB_NAME" -f "$BACKUP_DIR/${DB_NAME}.dump"

echo "Respaldando filestore (adjuntos)..."
if [ -d ".local/filestore/${DB_NAME}" ]; then
  tar -czf "$BACKUP_DIR/filestore_${DB_NAME}.tar.gz" -C .local/filestore "${DB_NAME}"
else
  echo "  (sin filestore para esta base, se omite)"
fi

echo "Listo: $BACKUP_DIR"
echo "Recomendado: copiar esta carpeta a un almacenamiento externo/off-site,"
echo "no dejarla solo en este Mac."
