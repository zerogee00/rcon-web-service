# 🔧 Slack Command Troubleshooting Guide

## 🎯 Issue Analysis

You mentioned two problems:
1. **Slack notifications don't have preview content** ✅ FIXED
2. **Can't list servers in the rcon channel** ← Let's fix this

## ✅ What I've Fixed

### 1. Slack Notification Previews
- **Problem**: Backup notifications had no preview content
- **Solution**: Updated notification format to include `"text"` field for previews
- **Test**: Run `./test_notification.sh` - should show preview in Slack now

### 2. Markdown Formatting  
- **Problem**: Double backslashes (`\\n`) causing formatting issues
- **Solution**: Fixed all Slack response formatting 
- **Result**: Clean, properly formatted messages

## 🔍 Server Listing Issue - Possible Causes

### **Most Likely**: Missing Slack Command Configuration

Your RCON service has these endpoints ready:
```
✅ /slack/mc       → for /mc commands
✅ /slack/players  → for /players commands  
✅ /slack/servers  → for /servers commands
✅ /slack/backup   → for /backup commands
```

But Slack needs each slash command configured in your app settings.

## 🛠️ How to Fix Server Listing

### **Option 1: Use `/mc servers` (Should Work Now)**
If `/mc` is already configured in Slack:
```
/mc servers
```
This will show the server list.

### **Option 2: Configure `/servers` as Separate Command**
In your Slack App settings, add a new slash command:
- **Command**: `/servers`  
- **Request URL**: `https://your-domain.com/slack/servers`
- **Short Description**: List available Minecraft servers

### **Option 3: Use Alternative Commands**
These might already be working:
```
/mc servers          # List servers via mc command
/backup list         # List servers for backup
/players             # If configured, shows players
```

## 🧪 Testing Your Setup

### **Test 1: Check What Commands Work**
Try these in Slack to see which are configured:
```bash
/mc help             # Should show help menu
/mc servers          # Should show server list  
/backup list         # Should show servers for backup
/players             # Might work if configured
/servers             # Might not work if not configured
```

### **Test 2: Check Service Response**
```bash
# From server, check if endpoints respond
curl -X GET http://localhost:5000/health
# Should return: {"status":"healthy","timestamp":...}
```

### **Test 3: Monitor Logs**  
```bash
# Watch for Slack requests
journalctl -u rcon-web -f
# Then try commands in Slack
```

## 📋 Current Working Commands

Based on your service configuration:

### ✅ `/mc` Commands (If configured in Slack)
```
/mc servers                    # ← This should list your servers!
/mc list                       # List players (will prompt for server)
/mc 7eaa7ab6 list             # List players on specific server
/mc help                       # Show help
```

### ✅ `/backup` Commands (If configured in Slack)  
```
/backup list                   # ← This also lists servers!
/backup status                 # Show backup activity
/backup incremental            # Start incremental backup
/backup full                   # Start full backup
```

### ❓ Standalone Commands (Need Slack Configuration)
```
/servers                       # Needs separate Slack app config
/players                       # Needs separate Slack app config
```

## 🎯 Quick Fix: Try These Commands

**Instead of `/servers`, try:**
```
/mc servers                    # Most likely to work
/backup list                   # Alternative that shows servers
```

## 🔧 Slack App Configuration Checklist

To add missing commands, go to your Slack App settings and ensure:

1. **Slash Commands Section**:
   - `/mc` → `https://your-domain/slack/mc` ✅
   - `/backup` → `https://your-domain/slack/backup` ✅ 
   - `/servers` → `https://your-domain/slack/servers` ❓
   - `/players` → `https://your-domain/slack/players` ❓

2. **OAuth & Permissions**:
   - `commands` scope enabled ✅
   - Bot token installed in your workspace ✅

3. **Request URL Verification**:
   - All endpoints return 200 OK ✅
   - Signature verification working ✅

## 🎉 Expected Behavior After Fixes

### **Backup Notifications** (Should be fixed now)
- ✅ Show preview text in Slack
- ✅ Proper formatting with colors
- ✅ Rich attachments with details

### **Server Listing** 
- `/mc servers` should work and show:
```
👾 **Available Servers**

**Cactus 🌵  Truck 🛻**
ID: `7eaa7ab6`  
Port: 25576

**CactusTruckLanWorld**
ID: `b46f4016`
Port: 25581

**I am  a  Survivor: OddMine: Survival!**
ID: `e6a4f515`
Port: 25580
```

## 🚀 Next Steps

1. **Try `/mc servers` first** - most likely to work
2. **Check Slack app configuration** for missing commands
3. **Monitor logs** while testing: `journalctl -u rcon-web -f`
4. **Test backup notifications** with improved previews

Let me know which commands work and I can help configure the missing ones! 🎯
