# Backup Integration with RCON Web Service

## Overview
The backup system has been successfully integrated into the RCON Web Service, allowing you to manage Minecraft server backups directly from Slack.

## Features Added
✅ **Slack Integration**: Trigger backups via Slack commands  
✅ **Single Server Backups**: Target specific servers  
✅ **Full/Incremental Backups**: Choose backup type  
✅ **Cloud Upload**: Automatic upload to Google Drive  
✅ **Status Monitoring**: Check backup logs and status  
✅ **Cleanup Management**: Remove old backups  
✅ **Admin-Only Access**: Secure backup operations  

## Files Added/Modified

### New Files:
- `~/rcon-web-service/backup.sh` - Main backup script (copied from /var/lib/pufferpanel)
- `~/rcon-web-service/backup_single_server.sh` - Wrapper for single server backups
- `~/rcon-web-service/BACKUP_INTEGRATION.md` - This documentation

### Modified Files:
- `~/rcon-web-service/app.py` - Added backup endpoints and handlers
- `~/rcon-web-service/app.py.backup.before_backup_integration` - Backup of original app.py

## Slack Commands

### Basic Usage
```
/backup                    # Show help menu
/backup list              # List all available servers
/backup status            # Show recent backup activity
```

### Incremental Backups (Fast, No Cloud Upload)
```
/backup incremental                    # Backup all servers (incremental)
/backup incremental 7eaa7ab6          # Backup specific server (incremental)
```

### Full Backups (Complete, With Cloud Upload)
```
/backup full                          # Backup all servers (full + cloud)
/backup full 7eaa7ab6                # Backup specific server (full + cloud)
```

### Maintenance
```
/backup cleanup           # Clean up old remote backups
```

## Backup Types Explained

### Incremental Backups
- **Speed**: Very fast (rsync-based)
- **Storage**: Local only (no cloud upload)
- **Use Case**: Daily automated backups
- **Location**: `/var/lib/pufferpanel/servers/backup/incremental/`

### Full Backups
- **Speed**: Slower (zip creation + upload)
- **Storage**: Local + Cloud (Google Drive)
- **Use Case**: Weekly/monthly archival backups
- **Location**: `/var/lib/pufferpanel/servers/backup/full/` + Cloud

## Security

### Admin-Only Access
- Only users listed in `CONFIG['admin_users']` can use backup commands
- Currently configured for: `doktorodd`
- Modify `app.py` line ~46 to add more admin users

### Command Validation
- Server IDs are validated against known servers
- Invalid commands return helpful error messages
- All backup operations are logged

## Technical Details

### Background Execution
- All backup operations run in background processes
- No blocking of Slack responses
- Progress monitored via logs

### Logging
- All backup activity logged to `/var/log/minecraft-backup.log`
- Viewable via `/backup status` command
- Includes timestamps and detailed status

### Cloud Integration
- Uses rclone for Google Drive upload
- Automatic cleanup of old backups (keeps 5 most recent per server)
- Configurable retention policies

## Configuration

### Backup Script Settings
Located in `~/rcon-web-service/backup.sh`:

```bash
# Retention Policy
MAX_REMOTE_BACKUPS=5      # Keep 5 backups per server on cloud
MAX_LOCAL_DAYS=3          # Keep local backups for 3 days

# CPU Limiting
CPU_LIMIT_PERCENT="40"    # Limit to 40% CPU usage
NICE_LEVEL="15"           # Lower process priority

# Cloud Storage
RCLONE_REMOTE="gdrive-personal:mc-backups"  # Google Drive location
```

### Slack Notifications
- Configured webhook URL for notifications
- Status updates sent to Slack automatically
- Success/failure notifications included

## Troubleshooting

### Common Issues

1. **"Backup script not found" Error**
   - Ensure `backup.sh` exists in `/root/rcon-web-service/`
   - Check file permissions: `chmod +x ~/rcon-web-service/backup.sh`

2. **"Access denied" Error**
   - User not in admin list
   - Add username to `CONFIG['admin_users']` in `app.py`

3. **Cloud Upload Failures**
   - Check rclone configuration: `rclone ls gdrive-personal:`
   - Verify Google Drive permissions

### Log Checking
```bash
# View backup logs
tail -f /var/log/minecraft-backup.log

# Check service status
systemctl status rcon-web

# View service logs
journalctl -u rcon-web -f
```

## Testing

### Test Single Server Backup
```bash
# Test incremental backup for server 7eaa7ab6
~/rcon-web-service/backup_single_server.sh 7eaa7ab6 incremental

# Test full backup for server 7eaa7ab6
~/rcon-web-service/backup_single_server.sh 7eaa7ab6 full
```

### Test Via Slack
1. Use `/backup list` to see available servers
2. Try `/backup incremental 7eaa7ab6` for a quick test
3. Check `/backup status` to see progress

## Server Information

### Currently Configured Servers
- **7eaa7ab6** - Port 25576
- **b46f4016** - Port 25581  
- **e6a4f515** - Port 25580

### Adding New Servers
1. Add server config to `SERVERS` dict in `app.py`
2. Ensure server directory exists in `/var/lib/pufferpanel/servers/`
3. Restart service: `systemctl restart rcon-web`

## Maintenance Schedule

### Recommended Usage
- **Daily**: Incremental backups (automated via cron)
- **Weekly**: Full backups (manual via Slack)
- **Monthly**: Cleanup old backups

### Automation
The original backup script can still be used for cron automation:
```bash
# Add to crontab for daily incremental backups
0 2 * * * /var/lib/pufferpanel/backup.sh

# Weekly full backup cleanup
0 3 * * 0 /var/lib/pufferpanel/backup.sh --cleanup-remote
```

## Support
For issues or questions:
1. Check logs first: `/backup status` or `/var/log/minecraft-backup.log`
2. Verify service status: `systemctl status rcon-web`
3. Test backup scripts manually if needed
