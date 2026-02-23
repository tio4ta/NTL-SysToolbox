#!/bin/bash

DB_USER="admin_ntl"
DB_PASS="Ntl2026!"
DB_NAME="ntl_wms"
BACKUP_DIR="/backups/ntl"
REMOTE_USER="user"
REMOTE_SERVER="10.5.70.50"
DATE=$(date +%Y%m%d_%H%M)
ADMIN_EMAIL="corentin.lecoq89320@gmail.com"

export PATH=/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin

mkdir -p "$BACKUP_DIR"

echo "---Début du traitement NTL($DATE) ---"

echo "[1/4] Backup SQL et CSV..."
mysqldump -u "$DB_USER" -p"$DB_PASS" "$DB_NAME" > "$BACKUP_DIR/ntl_backup_$DATE.sql"


mariadb -u "$DB_USER" -p"$DB_PASS" -e "SELECT * FROM $DB_NAME.reception;" | tr '\t' ',' > "$BACKUP_DIR/reception_$DATE.csv"
mariadb -u "$DB_USER" -p"$DB_PASS" -e "SELECT * FROM $DB_NAME.expedition;" | tr '\t' ',' > "$BACKUP_DIR/expedition_$DATE.csv"

echo "[2/4] Transfert vers le serveur miroir $REMOTE_SERVER..."

if scp "$BACKUP_DIR"/*"$DATE"* "$REMOTE_USER@$REMOTE_SERVER:$BACKUP_DIR/"; then

    echo "[3/4] Restauration sur le miroir.."
    ssh "$REMOTE_USER@$REMOTE_SERVER" "mysql -u $DB_USER -p$DB_PASS $DB_NAME < $BACKUP_DIR/ntl_backup_$DATE.sql"

    RES_SYNC="SUCCÈS"
else
    RES_SYNC="ÉCHEC"
fi

find "$BACKUP_DIR" -type f -mtime +30 -delete

echo "[4/4] Envoi de l'email avec pièces jointes.."

MESSAGE="Rapport de sauvegarde NTL du $DATE. Statut : $RES_SYNC"

echo "$MESSAGE" | mutt -s "Rapport NTL $DATE $RES_SYNC" -a "$BACKUP_DIR/reception_$DATE.csv" -a "$BACKUP_DIR/expedition_$DATE.csv" -- "$ADMIN_EMAIL"

echo "--- TRAITEMENT TERMINÉ ---"
