# Smart Document Assistant - Change Log & Recovery Guide

## Version History & Complete Code Archive

> **Note:** Full code snapshots are preserved in Git history. This changelog contains only version summaries and key features for easier reading.

### Version 4.2.0 - Personal AI Profiles (2025-07-28)

**Personalized AI Context System**

**Major Features:**
- Personal profile system for customized AI responses
- Web interface at `/profile` for editing personal context
- Users can tell the AI who they are and what they do
- Automatically applies personal context to all voice/search queries
- Mobile/iOS automatically uses profiles via user parameter

**Technical:**
- New `user_profiles.json` stores personal context
- Profile data integrated into AI prompt generation
- Preferences for response style and detail level

### Version 4.1.0 - Voice Commands & Natural Language (2025-07-27)

**Voice Assistant Optimization**

**Major Features:**
- Natural language command recognition ("What's new with...", "Give me an update on...")
- Fixed AI to understand user intent instead of defining terms
- New `/voice` endpoint that properly handles iOS Shortcuts parameters
- Voice Commands Guide for team reference

**Fixes:**
- iOS Shortcuts now work reliably with user parameter
- AI no longer explains what "review" means when asked to review documents

### Version 4.0.0 - User Authentication & Team Access (2025-07-27)

**Complete Multi-User System**

**Major Features:**
- User authentication with Flask-Login
- Each user only sees their folder + WMA Team folder
- Admin panel at `/admin` for user management
- Password change functionality
- All 13 team members pre-configured
- Case-insensitive username handling

**Technical:**
- Lowercase usernames throughout system
- Fixed bcrypt password compatibility issues
- iOS Shortcuts work without login via user parameter

### Version 3.4.0 - Smart Folder Prioritization (2025-07-27)

**Personalized Search Results**

**Major Features:**
- User-specific folder prioritization
- Search user's folder first (2x weight), then team folder
- Support for all 13 team members with individual folders
- Web interface with user selection dropdown
- iOS Shortcuts support with &user= parameter

### Version 3.3.2 - OpenAI Integration (2025-07-27)

**AI-Powered Summaries with GPT-4o-mini**

**Major Features:**
- Replaced Claude with OpenAI GPT-4o-mini
- Fixed Railway proxy issues with custom httpx client
- Intelligent document summarization
- Natural language responses optimized for voice

**Technical Fixes:**
- Resolved Railway environment proxy injection
- Custom httpx client with trust_env=False
- OpenAI 1.35.0 compatibility

### Version 3.3.0 - Google Drive Integration Complete (2025-07-26)

**FINAL MILESTONE - Full Google Drive Search via iOS Shortcuts!**

**Major Features:**
- Complete Google Drive integration with OAuth 2.0
- Searches both local files AND Google Drive documents
- Supports PDF, DOCX, TXT, and Google Docs formats
- Auto-refreshes expired tokens
- Works seamlessly with iOS Shortcuts
- New `app_flask_drive.py` with Drive API integration
- Status endpoint at `/api/status` to check Drive connection

**Setup Requirements:**
- Google Cloud Console project with Drive API enabled
- OAuth 2.0 credentials configured
- Environment variables: GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, GOOGLE_REFRESH_TOKEN, GOOGLE_TOKEN
- See GOOGLE_DRIVE_SETUP.md for complete instructions

### Version 3.2.0 - Flask API with Working iOS Shortcuts (2025-07-26)

**BREAKTHROUGH - iOS Shortcuts Finally Working!**

**Major Features:**
- Replaced Streamlit with Flask for true API endpoints
- iOS Shortcuts can now parse responses correctly
- Plain text API endpoint at `/api/search/text`
- Two-tap operation: dictate, then hear response
- Flask app serving multiple endpoints:
  - `/` - Browser interface
  - `/api/search` - JSON/text response
  - `/api/search/text` - Pure text for iOS

**iOS Shortcut Setup:**
1. Dictate text
2. Get contents of URL: `https://web-production-5c94.up.railway.app/api/search/text?q=[Dictated Text]`
3. Get text from Contents of URL
4. Speak Text

### Version 3.1.0 - Working Shortcuts Integration (2025-07-26)

**Major Features:**
- iOS Shortcuts with Dictate Text fully functional
- URL parameter integration fixed
- Voice input → Document search → Voice output complete

### Version 3.0.0 - Siri/Google Assistant Integration (2025-07-25)

**GAME CHANGER - True Hands-Free Operation**

**Major Features:**
- Direct integration with Siri Shortcuts and Google Assistant
- Zero taps required - just speak to Siri/Google
- URL parameter support for voice queries
- Auto-plays audio response
- Perfect for driving - completely hands-free

---

## Earlier Versions (2.x Series)

### Version 2.3.0 - Voice Trigger Word "GO" (2025-07-25)
- Added verbal trigger word to submit questions
- Prevents accidental submissions during natural pauses

### Version 2.2.0 - Final Reliable Voice Interface (2025-07-25)
- Simplified to use native mobile keyboard microphone
- Removed complex JavaScript that Streamlit was blocking

### Version 2.1.0 - Voice-First One-Click Interface (2025-07-25)
- Created voice-first interface with one-click operation
- Auto-submission after speaking
- Mobile-optimized with large microphone button

### Version 2.0.0 - Voice-Enabled Hybrid Architecture (2025-07-25)
- Migrated from Streamlit-only to FastAPI + Streamlit hybrid
- Added voice input via Web Speech API
- Added voice output via gTTS and ElevenLabs

---

## Recovery Procedures

### Rolling Back to Previous Version
```bash
# View commit history
git log --oneline

# Rollback to specific commit
git checkout <commit-hash>

# Or revert last commit
git revert HEAD
```

### Troubleshooting Shortcuts (v3.1.0+)

**If no voice response:**
1. Check Railway deployment is active
2. Test URL in browser: `https://web-production-5c94.up.railway.app?q=test`
3. Ensure "Get Text from Input" is between Get Contents and Speak
4. Verify Speak uses "Text" not "Contents of URL"

**If getting HTML instead of text:**
- Add "Get Text from Input" action after Get Contents
- Make sure correct app file is deployed (check Procfile)

**Testing document search:**
- Documents must be .txt files in app/docs folder
- Try queries like "AI agent", "Ford", "sales journey"
- App returns first 2 matching snippets

### Common Fixes

**Backend not connecting:**
- Check BACKEND_URL in environment variables
- Ensure both services are running
- Check CORS settings in FastAPI

**Voice input not working:**
- Browser must support Web Speech API (Chrome/Edge)
- HTTPS required for production
- Check microphone permissions

**Audio playback issues:**
- Check audio synthesis provider settings
- Verify API keys are correct
- Test with gTTS first (no API key needed)

---

## Deployment Checklist

- [ ] Push code to GitHub
- [ ] Set up Railway project
- [ ] Add environment variables in Railway
- [ ] Connect GitHub repo to Railway
- [ ] Enable auto-deploy
- [ ] Test voice input/output
- [ ] Verify mobile responsiveness

---

Last Updated: 2025-07-28
Maintained by: Jeff Hunter (rjhunter3789)