#!/bin/bash

# Wrapper script for single server backup
# Usage: ./backup_single_server.sh <server_id> <backup_type>
# backup_type: incremental or full

SERVER_ID="$1"
BACKUP_TYPE="$2"

if [ -z "$SERVER_ID" ] || [ -z "$BACKUP_TYPE" ]; then
    echo "Usage: $0 <server_id> <backup_type>"
    echo "backup_type: incremental or full"
    exit 1
fi

# Find the main backup script
BACKUP_SCRIPT="$(dirname "$0")/backup.sh"
if [ ! -f "$BACKUP_SCRIPT" ]; then
    BACKUP_SCRIPT="/var/lib/pufferpanel/backup.sh"
fi

if [ ! -f "$BACKUP_SCRIPT" ]; then
    echo "Error: Backup script not found"
    exit 1
fi

# Set up environment (matching main script)
export TIMESTAMP=$(date +"%Y-%m-%d_%H-%M-%S")
export LOG_FILE="/var/log/minecraft-backup.log"
export SERVER_ROOT="/var/lib/pufferpanel/servers"
export BACKUP_ROOT="$SERVER_ROOT/backup"
export RCLONE_REMOTE="gdrive-personal:mc-backups"
export INCREMENTAL_DIR="$BACKUP_ROOT/incremental"
export FULL_DIR="$BACKUP_ROOT/full"

# Retention and CPU limiting (matching main script)
export MAX_REMOTE_BACKUPS=5
export MAX_LOCAL_DAYS=3
export CPU_LIMIT_PERCENT="40"
export NICE_LEVEL="15"
export IONICE_CLASS="3"

# Slack configuration (matching main script)
export SLACK_WEBHOOK_URL="${SLACK_WEBHOOK_URL:-}"
export SLACK_ENABLED="true"

# Create directories
mkdir -p "$BACKUP_ROOT" "$INCREMENTAL_DIR" "$FULL_DIR"

# Extract functions from the main script
extract_functions() {
    local script="$1"
    # Extract all functions and their dependencies
    sed -n '/^# === LOGGING ===/,/^# === MAIN SCRIPT ===/p' "$script" | head -n -1
}

# Source the functions by evaluating them
eval "$(extract_functions "$BACKUP_SCRIPT")"

# Log the start
log "🎯 Single server backup started for $SERVER_ID ($BACKUP_TYPE) via Slack/Web"

# Validate server exists
if [ ! -d "$SERVER_ROOT/$SERVER_ID" ]; then
    log "❌ Server directory $SERVER_ROOT/$SERVER_ID does not exist"
    exit 1
fi

# Run the appropriate backup
if [ "$BACKUP_TYPE" = "incremental" ]; then
    incremental_backup_server "$SERVER_ID"
    exit_code=$?
elif [ "$BACKUP_TYPE" = "full" ]; then
    backup_server "$SERVER_ID"
    exit_code=$?
else
    log "❌ Invalid backup type: $BACKUP_TYPE. Use 'incremental' or 'full'"
    exit 1
fi

if [ $exit_code -eq 0 ]; then
    log "✅ Single server backup completed successfully for $SERVER_ID ($BACKUP_TYPE)"
else
    log "❌ Single server backup failed for $SERVER_ID ($BACKUP_TYPE)"
fi

exit $exit_code
