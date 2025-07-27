# Mobile Setup Guide for Smart Document Assistant

This guide will help you set up voice commands on your phone to quickly access your Smart Document Assistant.

## What You'll Need
- Your username for the Smart Document Assistant
- Your phone (iPhone or Android)
- 5 minutes to set up

---

## For iPhone Users (Siri Shortcuts)

### Step-by-Step Instructions:

1. **Open the Shortcuts app** on your iPhone
   - Look for the colorful square icon
   - If you don't have it, download it free from the App Store

2. **Create a new shortcut**
   - Tap the "+" button in the top right corner

3. **Add the web action**
   - Tap "Add Action"
   - Search for "Open URLs"
   - Select "Open URLs"

4. **Enter your personal URL**
   - In the URL field, type:
   ```
   https://your-app-url.com/voice?user=YOUR_USERNAME
   ```
   - Replace `YOUR_USERNAME` with your actual username
   - Replace `your-app-url.com` with the actual domain

5. **Name your shortcut**
   - Tap the settings icon (three dots) at the top
   - Tap "Add to Siri"
   - Record a phrase like "Open my documents" or "Start document assistant"

6. **Save and test**
   - Tap "Done"
   - Say "Hey Siri" followed by your phrase
   - Your Smart Document Assistant should open!

---

## For Android Users

### Option 1: Google Assistant Routine (Easiest)

1. **Open Google Assistant settings**
   - Say "Hey Google, open Assistant settings"
   - Or open the Google app and tap your profile picture → Settings → Google Assistant

2. **Create a routine**
   - Tap "Routines"
   - Tap "+" or "New" button

3. **Set up the trigger**
   - Tap "Add starter"
   - Choose "Voice"
   - Type what you want to say, like "Open my documents"
   - Tap the checkmark

4. **Add the action**
   - Tap "Add action"
   - Scroll down and tap "Open app or website"
   - Enter your URL:
   ```
   https://your-app-url.com/voice?user=YOUR_USERNAME
   ```
   - Replace `YOUR_USERNAME` with your actual username
   - Replace `your-app-url.com` with the actual domain

5. **Save the routine**
   - Tap "Save"
   - Test by saying "Hey Google" followed by your phrase

### Option 2: Browser Bookmark Shortcut (Simple Alternative)

1. **Open your browser** (Chrome, Firefox, etc.)

2. **Go to your personal URL**
   ```
   https://your-app-url.com/voice?user=YOUR_USERNAME
   ```

3. **Add to home screen**
   - Tap the menu (three dots)
   - Select "Add to Home screen"
   - Name it "Document Assistant"
   - Tap "Add"

4. **Use the shortcut**
   - Find the new icon on your home screen
   - Tap it to open your assistant instantly

### Option 3: Using Tasker (Advanced Users)

1. **Install Tasker** from Google Play Store (paid app)

2. **Create a new task**
   - Open Tasker
   - Tap "+" → "Task"
   - Name it "Document Assistant"

3. **Add browse action**
   - Tap "+" to add action
   - Select "Net" → "Browse URL"
   - Enter your URL:
   ```
   https://your-app-url.com/voice?user=YOUR_USERNAME
   ```

4. **Create a voice trigger**
   - Go back to main screen
   - Tap "Profiles" → "+"
   - Choose "Event" → "Plugin" → "AutoVoice"
   - Set your voice command

---

## Important Notes

- **Privacy**: Your username is part of the URL, so anyone with the link can access your assistant
- **Internet Required**: You need an active internet connection for this to work
- **First Time**: The first time you use the shortcut, your browser may ask for microphone permissions - tap "Allow"

## Troubleshooting

**"It's not working!"**
- Check your internet connection
- Make sure you replaced YOUR_USERNAME with your actual username
- Try opening the URL directly in your browser first

**"Siri/Google doesn't understand me"**
- Speak clearly and slowly
- Try a simpler phrase like "My documents"
- Make sure your phone isn't on silent mode

**"The page won't load"**
- Double-check the URL is correct
- Ensure you have the right username
- Try refreshing the page

## Need More Help?

Contact your Smart Document Assistant administrator with:
- Your phone type (iPhone/Android)
- What step you're stuck on
- Any error messages you see