# 📱 Siri Shortcut Setup Guide for Smart Document Assistant

## Complete Hands-Free Voice Control While Driving 🚗

### What You'll Be Able to Do:
- Say: "Hey Siri, ask my assistant about Q2 sales"
- Say: "Hey Siri, ask my assistant to summarize the dealer report"
- Completely hands-free - perfect for driving!

---

## Step-by-Step Setup (5 minutes)

### Step 1: Copy the Base URL
```
https://web-production-5c94.up.railway.app
```

### Step 2: Open Shortcuts App on iPhone
- Find the purple Shortcuts app icon
- Tap to open

### Step 3: Create New Shortcut
1. Tap the **+** button (top right)
2. Tap **Add Action**

### Step 4: Add Text Action
1. Search for **"Text"**
2. Select **Text** action
3. In the text field, type exactly: `Spoken Text`
4. Tap **Done**

### Step 5: Add URL Action
1. Tap **+** to add another action
2. Search for **"URL"**
3. Select **URL** action
4. In the URL field, type:
   ```
   https://web-production-5c94.up.railway.app?q=
   ```
5. Right after the `=`, tap **Variables**
6. Select **Spoken Text** (from Step 4)

### Step 6: Add Get Contents Action
1. Tap **+** to add another action
2. Search for **"Get Contents"**
3. Select **Get Contents of URL**
4. It should automatically use the URL from Step 5

### Step 7: Add to Siri
1. Tap the settings icon (☰) at top
2. Tap **Add to Siri**
3. Record your phrase:
   - "Ask my assistant"
   - or "Search documents"
   - or "Question for assistant"
4. Tap **Done**

### Step 8: Name Your Shortcut
1. Give it a name like "Document Assistant"
2. Tap **Done** (top right)

---

## 🎉 You're Done! Test It:

### Test Examples:
- "Hey Siri, ask my assistant what were last month's sales"
- "Hey Siri, ask my assistant to summarize the Q2 report"
- "Hey Siri, ask my assistant about dealer performance"

### What Happens:
1. Siri listens to your question
2. Opens your assistant briefly
3. Shows and speaks the answer
4. You never touch the phone!

---

## Troubleshooting

### If Siri doesn't understand:
- Make sure you say the exact phrase you recorded
- Speak clearly after Siri recognizes the command
- Check your internet connection

### If the page doesn't load:
- Verify the URL is exactly: `https://web-production-5c94.up.railway.app?q=`
- Make sure there's no space before the `?q=`
- Check that Spoken Text variable is added after the `=`

### If no answer appears:
- The question might be too long
- Try a simpler question first
- Make sure the app is running on Railway

---

## Pro Tips 🚀

1. **Create Multiple Shortcuts** for common questions:
   - "Q2 Summary" → Always asks about Q2
   - "Sales Report" → Always asks about sales

2. **Use in CarPlay**:
   - Works perfectly with CarPlay
   - Voice response plays through car speakers

3. **Share with Team**:
   - Export your shortcut
   - Send to team members
   - They can import and use immediately

---

## Privacy & Security 🔒
- Your questions are processed securely
- No data is stored after the session
- Only you can access your shortcuts
- Works over encrypted HTTPS

---

Enjoy truly hands-free document search while driving safely! 🚗🎙️