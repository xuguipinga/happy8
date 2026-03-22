#!/bin/bash
# --------------------------------------------------------
# 企业级数据库自动备份脚本
# --------------------------------------------------------

BACKUP_DIR="/opt/mysql_backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
CONTAINER_NAME="ecommerce_db"
DB_NAME="ecommerce_admin"
PASSWORD="root_password_123"

mkdir -p $BACKUP_DIR

echo "Starting backup of $DB_NAME..."

# 使用 docker exec 运行 mysqldump
docker exec $CONTAINER_NAME /usr/bin/mysqldump -u root --password=$PASSWORD $DB_NAME > $BACKUP_DIR/${DB_NAME}_$TIMESTAMP.sql

# 压缩备份
gzip $BACKUP_DIR/${DB_NAME}_$TIMESTAMP.sql

# 删除超过 30 天的旧备份
find $BACKUP_DIR -name "*.sql.gz" -mtime +30 -delete

echo "Backup completed: $BACKUP_DIR/${DB_NAME}_$TIMESTAMP.sql.gz"
