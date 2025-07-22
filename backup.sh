#!/bin/bash

# === CONFIG ===
TIMESTAMP=$(date +"%Y-%m-%d_%H-%M-%S")
LOG_FILE="/var/log/minecraft-backup.log"
SERVER_ROOT="/var/lib/pufferpanel/servers"
BACKUP_ROOT="$SERVER_ROOT/backup"
RCLONE_REMOTE="gdrive-personal:mc-backups"
INCREMENTAL_DIR="$BACKUP_ROOT/incremental"
FULL_DIR="$BACKUP_ROOT/full"

# === CPU LIMITING CONFIGURATION ===
CPU_LIMIT_PERCENT="40"  # Limit to 40% of one CPU core
NICE_LEVEL="15"         # Lower priority (0-19, higher = lower priority)
IONICE_CLASS="3"        # Idle I/O priority class

# === SLACK CONFIGURATION ===
# Can be set via environment variable or command line argument
SLACK_WEBHOOK_URL="${BACKUP_SLACK_WEBHOOK_URL:-$SLACK_WEBHOOK_URL}"
SLACK_ENABLED="true"

# Check for webhook URL from command line arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --slack-url)
      SLACK_WEBHOOK_URL="$2"
      shift 2
      ;;
    --disable-slack)
      SLACK_ENABLED="false"
      shift
      ;;
    -i|--interactive)
      INTERACTIVE_MODE=true
      shift
      ;;
    *)
      shift
      ;;
  esac
done

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

# === ENHANCED SLACK NOTIFICATION FUNCTIONS ===
notify_slack() {
  local message="$1"
  local status="$2"
  local color="$3"
  local preview_text="$4"
  
  # Skip if Slack is disabled or webhook URL is not set
  if [ "$SLACK_ENABLED" != "true" ] || [ -z "$SLACK_WEBHOOK_URL" ]; then
    return 0
  fi
  
  # Enhanced payload with unfurl_links and unfurl_media for better previews
  local payload=$(cat <<PAYLOAD
{
  "text": "$preview_text",
  "unfurl_links": true,
  "unfurl_media": true,
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
      "footer_icon": "https://cdn-icons-png.flaticon.com/512/2620/2620669.png",
      "ts": $(date +%s),
      "mrkdwn_in": ["text", "pretext", "fields"]
    }
  ]
}
PAYLOAD
)
  
  # Send the notification with enhanced error handling
  local response=$(curl -X POST -H 'Content-type: application/json' \
    --data "$payload" \
    "$SLACK_WEBHOOK_URL" \
    --silent --show-error --write-out "%{http_code}" 2>&1)
  
  local curl_status=$?
  local http_code="${response: -3}"
  
  if [ $curl_status -eq 0 ] && [ "$http_code" = "200" ]; then
    log "✅ Slack notification sent successfully"
  else
    log "⚠️  Failed to send Slack notification (curl exit code: $curl_status, HTTP: $http_code)"
    if [ -n "$response" ]; then
      log "   Response: ${response:0:-3}"
    fi
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
      display_name=$(echo "$display_name" | sed 's/§[0-9a-fA-F]//g' | sed 's/^"//;s/"$//' | sed 's/\\"//g' | sed 's/^[ \t]*//;s/[ \t]*$//' | head -c 40)
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
    display_name=$(grep "^motd=" "$SERVER_ROOT/$server_id/server.properties" 2>/dev/null | cut -d'=' -f2- | sed 's/§[0-9a-fA-F]//g' | sed 's/^[ \t]*//;s/[ \t]*$//' | head -c 40)
  fi
  
  # If still no name, use server ID
  if [ -z "$display_name" ]; then
    display_name="$server_id"
  fi
  
  echo "$display_name"
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
    notify_slack "✅ Incremental backup of *$display_name* (\`$server_id\`) completed successfully\n📦 *Size:* $size\n⏰ *Time:* $(date '+%H:%M:%S')" "success" "good" "✅ Backup completed: $display_name"
  else
    echo " ❌ Failed"
    log "❌ Incremental backup failed for $server_id"
    notify_slack "❌ Incremental backup of *$display_name* (\`$server_id\`) failed!\n⚠️ *Status:* Failed\n⏰ *Time:* $(date '+%H:%M:%S')" "error" "danger" "❌ Backup failed: $display_name"
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
        notify_slack "✅ Full backup of *$display_name* (\`$server_id\`) uploaded successfully\n📦 *Size:* $size\n☁️ *Location:* $RCLONE_REMOTE\n⏰ *Time:* $(date '+%H:%M:%S')" "success" "good" "✅ Backup uploaded: $display_name"
      else
        echo " ❌ Upload failed"
        log "❌ Upload failed"
        notify_slack "❌ Full backup of *$display_name* (\`$server_id\`) upload failed!\n📦 *Size:* $size\n☁️ *Target:* $RCLONE_REMOTE\n⚠️ *Status:* Upload Failed\n⏰ *Time:* $(date '+%H:%M:%S')" "error" "danger" "❌ Upload failed: $display_name"
      fi
    else
      echo " ❌ Failed to create backup"
      log "❌ Failed to create backup for $server_id"
      notify_slack "❌ Full backup creation failed for *$display_name* (\`$server_id\`)!\n⚠️ *Status:* Creation Failed\n⏰ *Time:* $(date '+%H:%M:%S')" "error" "danger" "❌ Backup creation failed: $display_name"
      [ -f "$backup_path" ] && rm -f "$backup_path"
    fi
  else
    echo " ⚠️  No backup items found"
    log "⚠️  No backup items found for $server_id"
    notify_slack "⚠️ No backup items found for *$display_name* (\`$server_id\`)\n📂 *Path:* $server_dir\n⏰ *Time:* $(date '+%H:%M:%S')" "warning" "warning" "⚠️ No backup items: $display_name"
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
    notify_slack "🚀 Starting full backup of *all servers*...\n📊 *Server Count:* ${#servers[@]}\n⏰ *Started:* $(date '+%H:%M:%S')" "info" "warning" "🚀 Starting full backup of all servers"
    
    for server_id in "${servers[@]}"; do
      backup_server "$server_id"
    done
    
    notify_slack "✅ Full backup of *all servers* completed successfully!\n📊 *Servers:* ${#servers[@]}\n⏰ *Completed:* $(date '+%H:%M:%S')" "success" "good" "✅ All servers backed up successfully"
  elif [ "$choice" -ge 1 ] && [ "$choice" -le "${#servers[@]}" ]; then
    local selected_server_id=${servers[$((choice-1))]}
    echo "📦 Backing up ${server_names[$((choice-1))]} ($selected_server_id)..."
    log "📦 Full backup of selected server: $selected_server_id"
    notify_slack "🚀 Starting full backup of *${server_names[$((choice-1))]}* (\`$selected_server_id\`)...\n⏰ *Started:* $(date '+%H:%M:%S')" "info" "warning" "🚀 Starting backup: ${server_names[$((choice-1))]}"
    
    backup_server "$selected_server_id"
  else
    echo "❌ Invalid selection."
    log "❌ Invalid selection in interactive mode"
    exit 1
  fi
  
  # Cleanup
  echo "🧹 Cleaning up old local full backups..."
  log "🧹 Cleaning up old local full backups..."
  find "$FULL_DIR" -type f -name "*.zip" -mtime +3 -delete
  echo "✅ Cleanup complete!"
  log "✅ Full backup cleanup complete!"
}

# === MAIN SCRIPT ===
# Check if interactive mode is requested
if [[ "$INTERACTIVE_MODE" == "true" ]]; then
  interactive_mode
  exit 0
fi

# === AUTOMATIC MODE (Default - for crontab) ===
echo "🤖 Automatic Incremental Backup Mode"
echo "====================================="
echo ""
log "🤖 Automatic incremental backup mode started"

# Send start notification
notify_slack "🤖 Starting automatic incremental backup cycle...\n⏰ *Started:* $(date '+%H:%M:%S')" "info" "warning" "🤖 Starting automatic backup cycle"

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

# === CLEANUP: Delete incremental backups older than 3 days ===
log "🧹 Cleaning up old local incremental backups..."
find "$INCREMENTAL_DIR" -type d -mtime +3 -exec rm -rf {} \; 2>/dev/null

# === CLEANUP: Delete full backups older than 3 days ===
log "🧹 Cleaning up old local full backups..."
find "$FULL_DIR" -type f -name "*.zip" -mtime +3 -delete
log "✅ Full backup cleanup complete!"
log "✅ Incremental cleanup complete!"

echo "✅ Incremental backup cycle complete!"
log "✅ Incremental backup cycle complete!"

# Send completion summary
if [ $failed_backups -eq 0 ]; then
  notify_slack "✅ Incremental backup cycle *completed successfully*!\n📊 *Successful:* $successful_backups server(s)\n⏰ *Completed:* $(date '+%H:%M:%S')" "success" "good" "✅ Backup cycle completed successfully"
else
  notify_slack "⚠️ Incremental backup cycle completed *with issues*:\n📊 *Successful:* $successful_backups\n❌ *Failed:* $failed_backups\n⏰ *Completed:* $(date '+%H:%M:%S')" "warning" "warning" "⚠️ Backup cycle completed with issues"
fi
