#!/bin/bash

# === CONFIG ===
TIMESTAMP=$(date +"%Y-%m-%d_%H-%M-%S")
LOG_FILE="/var/log/minecraft-backup.log"
SERVER_ROOT="/var/lib/pufferpanel/servers"
BACKUP_ROOT="$SERVER_ROOT/backup"
RCLONE_REMOTE="gdrive-personal:mc-backups"
INCREMENTAL_DIR="$BACKUP_ROOT/incremental"
FULL_DIR="$BACKUP_ROOT/full"

# === RETENTION POLICY ===
MAX_REMOTE_BACKUPS=5  # Keep only 5 most recent backups per server on remote
MAX_LOCAL_DAYS=3      # Keep local backups for 3 days

# === CPU LIMITING CONFIGURATION ===
CPU_LIMIT_PERCENT="40"  # Limit to 40% of one CPU core
NICE_LEVEL="15"         # Lower priority (0-19, higher = lower priority)
IONICE_CLASS="3"        # Idle I/O priority class

# === SLACK CONFIGURATION ===
# Set your Slack webhook URL here
SLACK_WEBHOOK_URL="${SLACK_WEBHOOK_URL:-}"  # Set via environment variable
# Set to true to enable Slack notifications
SLACK_ENABLED="true"

mkdir -p "$BACKUP_ROOT" "$INCREMENTAL_DIR" "$FULL_DIR"

# === LOGGING ===
log() {
  echo "[$(date +"%Y-%m-%d %H:%M:%S")] $1" | tee -a "$LOG_FILE"
}

# === CPU-LIMITED EXECUTION FUNCTION ===
run_cpu_limited() {
  local command="$1"
  local description="$2"
  
  log "🔧 Running CPU-limited: $description"
  log "   └─ CPU limit: ${CPU_LIMIT_PERCENT}%, Nice: ${NICE_LEVEL}, I/O priority: idle"
  
  # Execute command with CPU and I/O limitations
  nice -n "$NICE_LEVEL" ionice -c "$IONICE_CLASS" \
    timeout 3600 cpulimit -l "$CPU_LIMIT_PERCENT" -- bash -c "$command"
  
  return $?
}

# === SLACK NOTIFICATION FUNCTIONS ===
notify_slack() {
  local message="$1"
  local status="$2"
  local color="$3"
  
  # Skip if Slack is disabled or webhook URL is not set
  if [ "$SLACK_ENABLED" != "true" ] || [ -z "$SLACK_WEBHOOK_URL" ]; then
    return 0
  fi
  
  # Construct the payload with color coding
  local payload=$(cat <<PAYLOAD
{
  "attachments": [
    {
      "color": "$color",
      "fields": [
        {
          "title": "Minecraft Backup Status",
          "value": "$message",
          "short": false
        }
      ],
      "footer": "PufferPanel Backup System",
      "ts": $(date +%s)
    }
  ]
}
PAYLOAD
)
  
  # Send the notification
  curl -X POST -H 'Content-type: application/json' \
    --data "$payload" \
    "$SLACK_WEBHOOK_URL" \
    --silent --show-error --fail > /dev/null 2>&1
  
  local curl_status=$?
  if [ $curl_status -ne 0 ]; then
    log "⚠️  Failed to send Slack notification (curl exit code: $curl_status)"
  fi
}

# === SPINNER ===
spinner() {
  local pid=$1
  local delay=0.1
  local spinstr='|/-\'
  while kill -0 $pid 2>/dev/null; do
    local temp=${spinstr#?}
    printf " [%c]  " "$spinstr"
    local spinstr=$temp${spinstr%$temp}
    printf "\b\b\b\b\b\b"
    sleep $delay
  done
  printf "    \b\b\b\b"
}

# === FUNCTION TO GET SERVER DISPLAY NAME ===
get_server_display_name() {
  local server_id="$1"
  local display_name=""
  
  # Try to get MOTD from PufferPanel JSON first (more specific)
  if [ -f "$SERVER_ROOT/$server_id.json" ]; then
    display_name=$(jq -r '.data.motd.value // empty' "$SERVER_ROOT/$server_id.json" 2>/dev/null)
    # Clean up Minecraft formatting codes, quotes, and spaces
    if [ -n "$display_name" ]; then
      display_name=$(echo "$display_name" | sed "s/§[0-9a-fA-F]//g"' | sed 's/^[ \t]*//;s/[ \t]*$//' | head -c 40)
    fi
  fi
  
  # If no MOTD found, try to get display name from PufferPanel JSON
  if [ -z "$display_name" ] && [ -f "$SERVER_ROOT/$server_id.json" ]; then
    display_name=$(jq -r '.display // empty' "$SERVER_ROOT/$server_id.json" 2>/dev/null)
    # Clean up any spaces here too
    if [ -n "$display_name" ]; then
      display_name=$(echo "$display_name" | sed 's/^[ \t]*//;s/[ \t]*$//')
    fi
  fi
  
  # If still no name, try to get MOTD from server.properties
  if [ -z "$display_name" ] && [ -f "$SERVER_ROOT/$server_id/server.properties" ]; then
    display_name=$(grep "^motd=" "$SERVER_ROOT/$server_id/server.properties" 2>/dev/null | cut -d'=' -f2- | sed "s/§[0-9a-fA-F]//g"' | sed 's/^[ \t]*//;s/[ \t]*$//' | head -c 40)
  fi
  
  # If still no name, use server ID
  if [ -z "$display_name" ]; then
    display_name="$server_id"
  fi
  
  echo "$display_name"
}

# === REMOTE CLEANUP FUNCTION ===
cleanup_remote_backups() {
  local server_id="$1"
  local display_name=$(get_server_display_name "$server_id")
  
  log "🧹 Cleaning up remote backups for $display_name ($server_id)"
  
  # Get list of remote backups for this server, sorted by date (newest first)
  local remote_files=$(rclone ls "$RCLONE_REMOTE" --include "server-${server_id}-*.zip" 2>/dev/null | sort -k2 -r | awk '{print $2}')
  
  if [ -z "$remote_files" ]; then
    log "   └─ No remote backups found for $server_id"
    return 0
  fi
  
  # Convert to array
  local files_array=()
  while IFS= read -r line; do
    [ -n "$line" ] && files_array+=("$line")
  done <<< "$remote_files"
  
  local total_files=${#files_array[@]}
  log "   └─ Found $total_files remote backup(s) for $server_id"
  
  # If we have more than MAX_REMOTE_BACKUPS, delete the oldest ones
  if [ $total_files -gt $MAX_REMOTE_BACKUPS ]; then
    local files_to_delete=$((total_files - MAX_REMOTE_BACKUPS))
    log "   └─ Deleting $files_to_delete oldest backup(s) (keeping $MAX_REMOTE_BACKUPS most recent)"
    
    # Delete the oldest files (they're at the end of the array since we sorted newest first)
    for ((i=MAX_REMOTE_BACKUPS; i<total_files; i++)); do
      local file_to_delete="${files_array[$i]}"
      log "   └─ Deleting: $file_to_delete"
      if rclone delete "$RCLONE_REMOTE/$file_to_delete" > /dev/null 2>&1; then
        log "   └─ ✅ Deleted: $file_to_delete"
      else
        log "   └─ ❌ Failed to delete: $file_to_delete"
      fi
    done
  else
    log "   └─ No cleanup needed (have $total_files, max is $MAX_REMOTE_BACKUPS)"
  fi
}

# === INCREMENTAL BACKUP FUNCTION ===
incremental_backup_server() {
  local server_id="$1"
  local server_dir="$SERVER_ROOT/$server_id"
  local display_name=$(get_server_display_name "$server_id")
  
  # Skip if directory doesn't exist
  if [ ! -d "$server_dir" ]; then
    log "⚠️  Server directory $server_dir does not exist, skipping..."
    return 1
  fi
  
  local dest="$INCREMENTAL_DIR/$server_id"
  
  echo -n "📂 Incremental backup of $display_name ($server_id)..."
  log "📂 Starting incremental backup of $display_name ($server_id)"
  
  # Run rsync in background with spinner
  run_cpu_limited "rsync -a --delete '$server_dir/' '$dest/' > /dev/null 2>&1" "rsync for $display_name" &
  local rsync_pid=$!
  spinner $rsync_pid
  wait $rsync_pid
  local rsync_status=$?
  
  if [ $rsync_status -eq 0 ]; then
    local size=$(du -sh "$dest" 2>/dev/null | cut -f1)
    echo " ✅ ($size)"
    log "✅ Incremental backup completed: $size"
    notify_slack "✅ Incremental backup of **$display_name** ($server_id) completed successfully: $size" "success" "good"
  else
    echo " ❌ Failed"
    log "❌ Incremental backup failed for $server_id"
    notify_slack "❌ Incremental backup of **$display_name** ($server_id) failed!" "error" "danger"
  fi
  
  echo ""
}

# === BACKUP FUNCTION ===
backup_server() {
  local server_id="$1"
  local server_dir="$SERVER_ROOT/$server_id"
  local display_name=$(get_server_display_name "$server_id")
  
  # Skip if directory doesn't exist
  if [ ! -d "$server_dir" ]; then
    log "⚠️  Server directory $server_dir does not exist, skipping..."
    return 1
  fi
  
  local backup_name="server-${server_id}-$TIMESTAMP.zip"
  local backup_path="$FULL_DIR/$backup_name"

  echo -n "📦 Full backup of $display_name ($server_id)..."
  log "📦 Starting full backup of $display_name ($server_id)"

  # Build list of files/directories to backup
  local backup_items=()
  
  # Find all world directories (containing level.dat)
  for dir in "$server_dir"*/ ; do
    if [ -d "$dir" ] && [[ -f "$dir/level.dat" ]]; then
      # Get relative path from server root
      rel_path=$(realpath --relative-to="$SERVER_ROOT" "$dir")
      backup_items+=("$rel_path")
    fi
  done
  
  # Add other important files/directories if they exist (with relative paths)
  [ -d "$server_dir/plugins" ] && backup_items+=("$server_id/plugins")
  [ -f "$server_dir/server.properties" ] && backup_items+=("$server_id/server.properties")
  [ -f "$server_dir/whitelist.json" ] && backup_items+=("$server_id/whitelist.json")
  [ -f "$server_dir/banned-players.json" ] && backup_items+=("$server_id/banned-players.json")
  [ -f "$server_dir/banned-ips.json" ] && backup_items+=("$server_id/banned-ips.json")
  [ -f "$server_dir/ops.json" ] && backup_items+=("$server_id/ops.json")
  
  # Add PufferPanel server config JSON file
  [ -f "$SERVER_ROOT/$server_id.json" ] && backup_items+=("$server_id.json")
  
  # Only create backup if there are items to backup
  if [ ${#backup_items[@]} -gt 0 ]; then
    # Create the zip file with spinner
    run_cpu_limited "cd '$SERVER_ROOT' && zip -r '$backup_path' $(printf '%s ' "${backup_items[@]}") > /dev/null 2>&1" "zip creation for $display_name" &
    local zip_pid=$!
    spinner $zip_pid
    wait $zip_pid
    local zip_status=$?
    
    if [ $zip_status -eq 0 ] && [ -f "$backup_path" ] && [ -s "$backup_path" ]; then
      local size=$(du -h "$backup_path" 2>/dev/null | cut -f1)
      echo " ✅ ($size)"
      log "✅ Created full backup: $backup_name ($size)"
      
      echo -n "☁️  Uploading to $RCLONE_REMOTE..."
      log "☁️  Uploading full backup to $RCLONE_REMOTE"
      
      if rclone copy "$backup_path" "$RCLONE_REMOTE" > /dev/null 2>&1; then
        echo " ✅ Upload successful"
        log "✅ Upload successful"
        notify_slack "✅ Full backup of **$display_name** ($server_id) uploaded successfully to $RCLONE_REMOTE: $size" "success" "good"
        
        # Clean up old remote backups after successful upload
        cleanup_remote_backups "$server_id"
      else
        echo " ❌ Upload failed"
        log "❌ Upload failed"
        notify_slack "❌ Full backup of **$display_name** ($server_id) upload failed to $RCLONE_REMOTE!" "error" "danger"
      fi
    else
      echo " ❌ Failed to create backup"
      log "❌ Failed to create backup for $server_id"
      notify_slack "❌ Full backup creation failed for **$display_name** ($server_id)!" "error" "danger"
      [ -f "$backup_path" ] && rm -f "$backup_path"
    fi
  else
    echo " ⚠️  No backup items found"
    log "⚠️  No backup items found for $server_id"
  fi
  
  echo ""
}

# === INTERACTIVE MODE ===
interactive_mode() {
  echo "🎮 Interactive Full Backup Mode"
  echo "==============================="
  echo ""
  log "🎮 Interactive full backup mode started"
  
  # Get list of available servers with display names
  local servers=()
  local server_names=()
  
  for server_dir in "$SERVER_ROOT"/*/; do
    [ -d "$server_dir" ] || continue
    local server_id=$(basename "$server_dir")
    
    # Skip the backup directory itself
    if [ "$server_id" = "backup" ]; then
      continue
    fi
    
    local display_name=$(get_server_display_name "$server_id")
    servers+=("$server_id")
    server_names+=("$display_name")
  done
  
  # Check if any servers were found
  if [ ${#servers[@]} -eq 0 ]; then
    echo "❌ No servers found in $SERVER_ROOT"
    log "❌ No servers found in $SERVER_ROOT"
    exit 1
  fi
  
  echo "📋 Available servers:"
  for i in "${!servers[@]}"; do
    echo "  $((i+1)). ${server_names[$i]} (${servers[$i]})"
  done
  
  echo ""
  echo "Select servers to backup:"
  echo "  $((${#servers[@]}+1)). ALL - Backup all servers"
  echo ""
  
  read -p "Enter your choice (1-$((${#servers[@]}+1))): " choice
  
  if [ "$choice" = "$((${#servers[@]}+1))" ]; then
    echo "📦 Backing up all servers..."
    log "📦 Full backup of all servers started"
    notify_slack "🚀 Starting full backup of all servers..." "info" "warning"
    
    for server_id in "${servers[@]}"; do
      backup_server "$server_id"
    done
    
    notify_slack "✅ Full backup of all servers completed successfully!" "success" "good"
  elif [ "$choice" -ge 1 ] && [ "$choice" -le "${#servers[@]}" ]; then
    local selected_server_id=${servers[$((choice-1))]}
    echo "📦 Backing up ${server_names[$((choice-1))]} ($selected_server_id)..."
    log "📦 Full backup of selected server: $selected_server_id"
    notify_slack "🚀 Starting full backup of **${server_names[$((choice-1))]}** ($selected_server_id)..." "info" "warning"
    
    backup_server "$selected_server_id"
  else
    echo "❌ Invalid selection."
    log "❌ Invalid selection in interactive mode"
    exit 1
  fi
  
  # Cleanup
  echo "🧹 Cleaning up old local full backups..."
  log "🧹 Cleaning up old local full backups..."
  find "$FULL_DIR" -type f -name "*.zip" -mtime +$MAX_LOCAL_DAYS -delete
  echo "✅ Cleanup complete!"
  log "✅ Full backup cleanup complete!"
}

# === CLEANUP ALL REMOTE BACKUPS (SPECIAL FUNCTION) ===
cleanup_all_remote_backups() {
  echo "🧹 Cleaning up all remote backups..."
  log "🧹 Starting cleanup of all remote backups"
  
  # Get all unique server IDs from remote backups
  local server_ids=$(rclone ls "$RCLONE_REMOTE" --include "server-*.zip" 2>/dev/null | awk '{print $2}' | sed 's/server-\(.*\)-[0-9].*\.zip/\1/' | sort -u)
  
  if [ -z "$server_ids" ]; then
    echo "   └─ No remote backups found to clean up"
    log "   └─ No remote backups found to clean up"
    return 0
  fi
  
  while IFS= read -r server_id; do
    [ -n "$server_id" ] && cleanup_remote_backups "$server_id"
  done <<< "$server_ids"
  
  echo "✅ Remote cleanup complete!"
  log "✅ Remote cleanup complete!"
}

# === MAIN SCRIPT ===
# Check if cleanup mode is requested
if [[ "$1" == "--cleanup-remote" ]]; then
  cleanup_all_remote_backups
  exit 0
fi

# Check if interactive mode is requested
if [[ "$1" == "-i" || "$1" == "--interactive" ]]; then
  interactive_mode
  exit 0
fi

# === AUTOMATIC MODE (Default - for crontab) ===
echo "🤖 Automatic Incremental Backup Mode"
echo "====================================="
echo ""
log "🤖 Automatic incremental backup mode started"

# Send start notification
notify_slack "🤖 Starting automatic incremental backup cycle..." "info" "warning"

# Track backup results
successful_backups=0
failed_backups=0

# Loop over all servers for incremental backup
for SERVER_DIR in "$SERVER_ROOT"/*/; do
  [ -d "$SERVER_DIR" ] || continue
  
  SERVER_ID=$(basename "$SERVER_DIR")
  
  # Skip the backup directory itself
  if [ "$SERVER_ID" = "backup" ]; then
    continue
  fi
  
  if incremental_backup_server "$SERVER_ID"; then
    ((successful_backups++))
  else
    ((failed_backups++))
  fi
done

# === CLEANUP: Delete incremental backups older than MAX_LOCAL_DAYS ===
log "🧹 Cleaning up old local incremental backups..."
find "$INCREMENTAL_DIR" -type d -mtime +$MAX_LOCAL_DAYS -exec rm -rf {} \; 2>/dev/null

# === CLEANUP: Delete full backups older than MAX_LOCAL_DAYS ===
log "🧹 Cleaning up old local full backups..."
find "$FULL_DIR" -type f -name "*.zip" -mtime +$MAX_LOCAL_DAYS -delete
log "✅ Local cleanup complete!"

echo "✅ Incremental backup cycle complete!"
log "✅ Incremental backup cycle complete!"

# Send completion summary
if [ $failed_backups -eq 0 ]; then
  notify_slack "✅ Incremental backup cycle completed successfully! $successful_backups server(s) backed up." "success" "good"
else
  notify_slack "⚠️ Incremental backup cycle completed with issues: $successful_backups successful, $failed_backups failed." "warning" "warning"
fi
