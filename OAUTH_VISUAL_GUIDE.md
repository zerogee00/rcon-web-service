# OAuth Permissions - Visual Step-by-Step Guide

## 🎯 Quick Reference

### Required Bot Token Scopes:
1. **commands** - For slash commands
2. **chat:write** - To send messages
3. **chat:write.public** - To send messages in any channel

---

## 📋 Step-by-Step Checklist

### Phase 1: Navigate to OAuth
- [ ] Go to https://api.slack.com/apps
- [ ] Select your app
- [ ] Click "OAuth & Permissions" in left sidebar

### Phase 2: Add Bot Token Scopes
- [ ] Scroll to "Scopes" section
- [ ] Find "Bot Token Scopes" (NOT User Token Scopes)
- [ ] Click "Add an OAuth Scope"

#### Add Each Scope:
- [ ] Add `commands`
  - Search: "commands"
  - Description: "Add shortcuts and/or slash commands that people can use"
  - Click "Add"

- [ ] Add `chat:write`
  - Search: "chat:write"  
  - Description: "Send messages as @YourBotName"
  - Click "Add"

- [ ] Add `chat:write.public`
  - Search: "chat:write.public"
  - Description: "Send messages to channels @YourBotName isn't a member of"
  - Click "Add"

### Phase 3: Install/Reinstall App
- [ ] Look for button at top of page:
  - First time: "Install to Workspace"
  - Adding scopes: "Reinstall to Workspace"
- [ ] Click the button
- [ ] Review permissions on Slack's page
- [ ] Click "Allow"

### Phase 4: Verify Installation
- [ ] Page shows "OAuth Tokens for Your Workspace"
- [ ] Bot User OAuth Token is displayed (starts with xoxb-)
- [ ] All 3 scopes are listed under "Bot Token Scopes"

---

## 🔍 What You'll See in Slack App Dashboard

### Before Adding Scopes:
```
Bot Token Scopes:
(No scopes added yet)
```

### After Adding All Scopes:
```
Bot Token Scopes:
✅ commands - Add shortcuts and/or slash commands that people can use
✅ chat:write - Send messages as @YourBotName  
✅ chat:write.public - Send messages to channels @YourBotName isn't a member of
```

### After Installation:
```
OAuth Tokens for Your Workspace:
Bot User OAuth Token: [YOUR_BOT_TOKEN_HERE]
```

---

## 🚨 Common Mistakes to Avoid

### ❌ Wrong Scope Section
- **DON'T** add to "User Token Scopes"
- **DO** add to "Bot Token Scopes"

### ❌ Missing Reinstall
- **DON'T** just add scopes and leave
- **DO** click "Reinstall to Workspace" after adding scopes

### ❌ Incomplete Scopes
- **DON'T** add only 1 or 2 scopes
- **DO** add all 3 required scopes

---

## ✅ Success Indicators

### In Slack App Dashboard:
- [ ] 3 scopes listed under Bot Token Scopes
- [ ] Bot User OAuth Token displayed
- [ ] "Installed to Workspace" status shown

### In Your Slack Workspace:
- [ ] App appears in Apps section
- [ ] `/mc` autocompletes when typing
- [ ] `/players` autocompletes when typing
- [ ] Commands show usage hints

### Test Commands:
- [ ] `/players` returns server status
- [ ] `/mc 7eaa7ab6 list` returns player list
- [ ] Responses appear in the channel

---

## 🔧 Troubleshooting OAuth Issues

### Issue: "This app isn't responding"
**Solution**: Check that all 3 scopes are added and app is reinstalled

### Issue: Commands don't autocomplete
**Solution**: Ensure `commands` scope is added and app is installed

### Issue: Bot doesn't respond
**Solution**: Check `chat:write` scope is added

### Issue: Bot can't post in channel
**Solution**: Add `chat:write.public` scope and reinstall

---

## 📞 Final Verification Script

Test your OAuth setup with these commands in Slack:

```
/players
/mc 7eaa7ab6 list
/mc b46f4016 tps
```

If all three work, your OAuth is configured correctly! 🎉
