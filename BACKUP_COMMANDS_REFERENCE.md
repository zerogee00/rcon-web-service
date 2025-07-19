# 🛠️ Backup Commands Quick Reference

## 🎯 Overview

Your RCON Web Service has comprehensive backup functionality ready for Slack integration. The `/slack/backup` endpoint is configured and waiting for the Slack slash command setup.

## 📋 Command Reference

### **Information & Status**
```bash
/backup              # Complete backup help guide
/backup list         # Show all servers available for backup  
/backup status       # View recent backup logs and activity
```

### **Incremental Backups** (Fast, Local Only)
```bash
/backup incremental                # Backup all servers (quick rsync)
/backup incremental 7eaa7ab6      # Backup Cactus Truck server
/backup incremental b46f4016      # Backup CactusTruckLanWorld
/backup incremental e6a4f515      # Backup OddMine Survival server
```
- ⚡ **Speed**: 30 seconds - 2 minutes
- 💾 **Storage**: Local only (`/var/lib/pufferpanel/servers/backup/incremental/`)  
- 🎯 **Use**: Daily automated backups

### **Full Backups** (Complete + Cloud Upload)
```bash
/backup full                       # Full backup all servers + upload
/backup full 7eaa7ab6             # Full backup Cactus Truck + upload
/backup full b46f4016             # Full backup CactusTruckLanWorld + upload
/backup full e6a4f515             # Full backup OddMine Survival + upload
```
- ⏱️ **Speed**: 2-10 minutes (depends on world size)
- ☁️ **Storage**: Local + Google Drive upload
- 🎯 **Use**: Weekly/monthly archival backups

### **Maintenance**
```bash
/backup cleanup       # Remove old remote backups (keeps 5 most recent per server)
```

## 🔐 Security & Permissions

- **Admin Only**: Only users in `admin_users` list can execute backup commands
- **Current Admin**: `doktorodd`
- **Signature Verification**: All requests validated with Slack signing secret
- **Endpoint**: `/slack/backup` (secured)

## 📊 Expected Behavior

### **Immediate Response** (from web service):
```
🚀 Starting incremental backup for **Cactus 🌵 Truck 🛻** (7eaa7ab6)...

This will run in the background. Check logs for completion status.
```

### **Progress Notification** (from backup script via webhook):
```
✅ Incremental backup of **Cactus 🌵 Truck 🛻** (7eaa7ab6) completed successfully: 1.2GB
```

## 🎯 Your Servers

| Server Name | ID | Port | Usage |
|-------------|----|----- |--------|
| **Cactus 🌵 Truck 🛻** | `7eaa7ab6` | 25576 | Main server |
| **CactusTruckLanWorld** | `b46f4016` | 25581 | LAN world |
| **I am a Survivor: OddMine: Survival!** | `e6a4f515` | 25580 | Survival server |

## 🎨 Slack App Configuration

### **Add this slash command to your Slack app:**

```
Command: /backup
Request URL: https://your-domain.com/slack/backup  
Short Description: Manage Minecraft server backups
Usage Hint: [list|status|incremental|full|cleanup] [server_id]
```

## 🧪 Testing Checklist

Once you add the `/backup` command to Slack:

1. ✅ **Basic Help**: `/backup` (should show comprehensive guide)
2. ✅ **Server List**: `/backup list` (should show your 3 servers)  
3. ✅ **Status Check**: `/backup status` (should show recent logs)
4. ✅ **Quick Backup**: `/backup incremental 7eaa7ab6` (should start backup)
5. ✅ **Check Notifications**: Look for webhook notifications in your backup channel

## 🚀 Ready to Go!

Your backup system is fully configured and ready. Just add the `/backup` slash command to your Slack app and you'll have complete backup management through Slack! 

The system will work seamlessly with your existing dual-channel setup:
- **RCON Channel**: `/mc` commands for gameplay
- **Backup Channel**: `/backup` commands for server management
