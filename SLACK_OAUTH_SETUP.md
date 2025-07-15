# Slack OAuth & Permissions Setup Guide

## Step-by-Step OAuth Configuration

### 1. Navigate to OAuth & Permissions
1. In your Slack app dashboard (https://api.slack.com/apps)
2. Select your app
3. In the left sidebar, click **"OAuth & Permissions"**

### 2. Bot Token Scopes Configuration

#### Required Scopes for RCON Bot
You need to add these **Bot Token Scopes** (NOT User Token Scopes):

1. **commands**
   - **Purpose**: Allows your app to create and respond to slash commands
   - **Why needed**: For `/mc` and `/players` commands to work

2. **chat:write**
   - **Purpose**: Post messages to channels and conversations
   - **Why needed**: To send RCON command responses back to Slack

3. **chat:write.public**
   - **Purpose**: Post messages to channels without joining them
   - **Why needed**: To respond in channels where the bot wasn't explicitly invited

#### How to Add Scopes:
1. Scroll down to **"Scopes"** section
2. Find **"Bot Token Scopes"** (NOT User Token Scopes)
3. Click **"Add an OAuth Scope"**
4. Search for and add each scope:
   - Type `commands` → Click "Add"
   - Type `chat:write` → Click "Add"  
   - Type `chat:write.public` → Click "Add"

### 3. Install App to Workspace

#### First Time Installation:
1. After adding scopes, you'll see **"Install to Workspace"** button at the top
2. Click **"Install to Workspace"**
3. You'll be redirected to Slack's authorization page
4. Review the permissions your app is requesting
5. Click **"Allow"** to authorize

#### Reinstalling (if you added new scopes):
1. If you added scopes to an already installed app, you'll see **"Reinstall to Workspace"**
2. Click **"Reinstall to Workspace"**
3. Authorize again with new permissions

### 4. Bot Token (Important!)

After installation, you'll get a **Bot User OAuth Token**:
- It starts with `xoxb-`
- **You don't need this token for your current setup** (our web service uses signing secret)
- Keep it secure anyway - don't share it

### 5. Verification Checklist

After setup, verify these items:

#### In OAuth & Permissions page:
- [ ] Bot Token Scopes shows: `commands`, `chat:write`, `chat:write.public`
- [ ] OAuth Tokens section shows "Bot User OAuth Token" (starts with xoxb-)
- [ ] Installation status shows "Installed to Workspace"

#### In your Slack workspace:
- [ ] Your app appears in the Apps section
- [ ] You can type `/mc` and `/players` and see them in the command list
- [ ] Commands show your usage hints when typing

### 6. Common Issues & Solutions

#### "Slash command not found"
- **Problem**: App not properly installed or missing `commands` scope
- **Solution**: Reinstall app with `commands` scope

#### "Bot can't post messages"
- **Problem**: Missing `chat:write` scope
- **Solution**: Add `chat:write` scope and reinstall

#### "Bot can't respond in channels"
- **Problem**: Missing `chat:write.public` scope
- **Solution**: Add `chat:write.public` scope and reinstall

#### "Permission denied" errors
- **Problem**: Scopes were added after installation
- **Solution**: Click "Reinstall to Workspace" to apply new permissions

### 7. Security Notes

- **Bot Token**: Keep your Bot User OAuth Token secure (though you don't need it for this setup)
- **Signing Secret**: Already configured in your service: `160d4303b6e7d262e71c01ef70726dd0`
- **Workspace Access**: Only authorized workspace members can use the commands

### 8. Testing OAuth Setup

After completing OAuth setup, test these:

1. **Command Recognition**: Type `/mc` in Slack - it should appear in autocomplete
2. **Response Permissions**: Run `/players` - bot should respond in the channel
3. **Error Handling**: Try `/mc invalid_server test` - should get error response

### 9. Final OAuth Configuration Summary

Your final OAuth & Permissions page should show:

```
Bot Token Scopes:
✅ commands - Add shortcuts and/or slash commands that people can use
✅ chat:write - Send messages as @YourBotName
✅ chat:write.public - Send messages to channels @YourBotName isn't a member of

OAuth Tokens for Your Workspace:
✅ Bot User OAuth Token: xoxb-xxxxxxxxx-xxxxxxxxx-xxxxxxxx
```

Once you see this configuration, your OAuth setup is complete! 🎉
