# RCON Web Service - Setup Complete! ✅

## Service Status
- **Service Name**: rcon-web.service
- **Status**: Active and running
- **Port**: 5000 (listening on all interfaces)
- **Workers**: 2 Gunicorn workers

## Configuration Details

### API Token
```
e0fb8b5ba296d6fc4c5b34fcab0eba8b7673e8ae12b48ddacad17d543d21dffd
```

### Slack Signing Secret
```
160d4303b6e7d262e71c01ef70726dd0
```

### Available Servers
- **7eaa7ab6**: Server 1 (Port 25576)
- **b46f4016**: Server 2 (Port 25581)  
- **e6a4f515**: Server 3 (Port 25580)

## API Endpoints

### Health Check
```
GET http://localhost:5000/health
```

### List Servers
```
GET http://localhost:5000/servers
Authorization: Bearer e0fb8b5ba296d6fc4c5b34fcab0eba8b7673e8ae12b48ddacad17d543d21dffd
```

### Execute RCON Command
```
POST http://localhost:5000/mc
Authorization: Bearer e0fb8b5ba296d6fc4c5b34fcab0eba8b7673e8ae12b48ddacad17d543d21dffd
Content-Type: application/json

{
    "server": "7eaa7ab6",
    "command": "list"
}
```

## Slack Slash Commands

Configure these in your Slack app:

### /mc Command
- **URL**: `https://YOUR-CLOUDFLARE-TUNNEL-DOMAIN.com/slack/mc`
- **Method**: POST
- **Usage**: `/mc <server_id> <command>`
- **Examples**:
  - `/mc 7eaa7ab6 list`
  - `/mc b46f4016 say Hello everyone!`
  - `/mc e6a4f515 tps`

### /players Command
- **URL**: `https://YOUR-CLOUDFLARE-TUNNEL-DOMAIN.com/slack/players`
- **Method**: POST
- **Usage**: `/players`
- **Description**: Shows player count for all servers

## Next Steps

1. **Configure Cloudflare Tunnel** to point to your server's port 5000
2. **Update Slack App** with the slash command URLs using your tunnel domain
3. **Test the integration** from Slack

## Management Commands

### Check Service Status
```bash
systemctl status rcon-web.service
```

### View Logs
```bash
journalctl -u rcon-web.service -f
```

### Restart Service
```bash
systemctl restart rcon-web.service
```

### Test API
```bash
cd /root/mc-web-service
./test_api.sh
```

## Files Created
- `/root/mc-web-service/app.py` - Main Flask application
- `/root/mc-web-service/requirements.txt` - Python dependencies
- `/etc/systemd/system/mc-web.service` - Systemd service file
- `/root/mc-web-service/test_api.sh` - Testing script
- `/root/mc-web-service/SETUP_COMPLETE.md` - This file

Your RCON web service is now fully configured and ready to use with Slack via Cloudflare tunnel!
