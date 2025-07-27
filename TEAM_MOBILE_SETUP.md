# WMA Document Assistant - Mobile Setup

Quick setup to use voice commands for document search on your phone.

## For iPhone Users

1. **Download Shortcuts app** (if you don't have it)
   - Free from App Store

2. **Create new shortcut**
   - Open Shortcuts → Tap "+" button

3. **Add these actions in order:**
   - Tap "Add Action"
   - Search "Dictate" → Select "Dictate Text"
   - Tap "Add Action" again
   - Search "URL" → Select "Get Contents of URL"
   
4. **Set up the URL**
   - In the URL field, enter:
   ```
   https://web-production-4dcb7c.up.railway.app/api/search/text?q={{Dictated Text}}&user=YOUR_NAME
   ```
   - Replace YOUR_NAME with your username (jeff, sarah, mike, etc.)
   - The {{Dictated Text}} should appear as a blue bubble

5. **Add display actions:**
   - Add Action → Search "Quick Look" → Select "Show in Quick Look"
   - Add Action → Search "Get Text" → Select "Get Text from Input"
   - Add Action → Search "Speak" → Select "Speak Text"

6. **Name it:**
   - Tap settings (3 dots) → "Add to Siri"
   - Say "Document Assistant" or your preferred phrase

## For Android Users

### Easy Option: Browser Bookmark

1. **Open Chrome**
2. **Go to:** 
   ```
   https://web-production-4dcb7c.up.railway.app
   ```
3. **Login with your credentials**
4. **Add to Home Screen:**
   - Tap 3 dots menu → "Add to Home screen"
   - Name it "WMA Documents"

### Voice Option: Google Assistant

1. **Open Google Assistant settings**
2. **Routines → New Routine**
3. **Add starter:** "Open my documents"
4. **Add action:** 
   - Open website
   - URL: `https://web-production-4dcb7c.up.railway.app`
5. **Save**

## Your Login Info
- **URL:** https://web-production-4dcb7c.up.railway.app
- **Username:** Your first name (lowercase)
- **Password:** Provided by Jeff

## Need Help?
Contact Jeff for your password or technical help.