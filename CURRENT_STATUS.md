# Smart Document Assistant - Current Status

## 🚀 System Overview

A voice-activated document search assistant that works with iOS Shortcuts and web browsers.

### Current Version: 4.1.0 (July 27, 2025)

## ✅ What's Working

### iOS Voice Commands
- Natural language queries via Siri Shortcuts
- Personalized results from user folders
- AI-powered summaries with GPT-4o-mini
- Text display and voice readout

### Web Access
- Secure login system at https://web-production-4dcb7c.up.railway.app
- Each user sees only their folder + team folder
- Admin panel for user management

### Supported Users (13 team members)
aaron, brody, dona, eric, grace, jeff, jessica, jill, john, jon, kirk, owen, paul

## 📱 iOS Shortcut URL Format

```
https://web-production-4dcb7c.up.railway.app/voice?user=YOUR_NAME&q={{Dictated Text}}
```

## 🔑 Key Features

1. **Google Drive Integration** - Searches all documents in user folders
2. **AI Summaries** - OpenAI GPT-4o-mini provides intelligent responses
3. **Natural Voice Commands** - "What's new with...", "Give me an update on..."
4. **Folder Prioritization** - Searches user's folder first, then team folder
5. **Multi-format Support** - PDF, DOCX, TXT, Google Docs

## 📂 Documentation Files

- `TEAM_MOBILE_SETUP.md` - iOS/Android setup instructions
- `VOICE_COMMANDS_GUIDE.md` - Natural language examples
- `CHANGELOG_AND_RECOVERY.md` - Version history
- `AUTH_SYSTEM_GUIDE.md` - Authentication details

## 🔧 Technical Stack

- **Backend**: Flask (Python)
- **AI**: OpenAI GPT-4o-mini
- **Storage**: Google Drive API
- **Hosting**: Railway
- **Auth**: Flask-Login with sessions

## 🎯 Recent Fixes

- iOS Shortcuts parameter handling (/voice endpoint)
- Case-insensitive usernames
- Natural language understanding
- No more "review" definitions!

## 📞 Support

Contact Jeff (admin) for:
- Password resets
- New user setup
- Technical issues