# iOS Shortcut Debugging Guide

## Problem
Your iOS Shortcut is fetching the URL but showing a blank Streamlit page in Quick Look.

## Root Causes Identified

1. **Query Parameter API Changes**: The app was using deprecated `st.experimental_get_query_params()` which may not work properly with iOS requests
2. **Complex HTML Output**: Streamlit generates complex HTML that iOS Quick Look may not render properly
3. **URL Encoding**: The query parameter might not be properly decoded

## Solutions Implemented

### 1. Updated app_shortcut_simple.py
- Added fallback methods to read query parameters
- Added URL decoding for proper parameter handling
- Uses `st.text()` for plain text output (better for iOS)

### 2. Created Alternative Versions

#### app_shortcut_debug.py
- Full debugging information
- Shows all parameter reading attempts
- Good for troubleshooting

#### app_shortcut_ios.py
- Minimal HTML output
- Optimized for iOS rendering
- Simple text-based responses

#### app_shortcut_text.py
- Returns pure plain text when query parameter present
- Best compatibility with iOS Shortcuts

## Testing Your Setup

### Method 1: Direct Browser Test
1. Open Safari on iPhone
2. Visit: `https://web-production-5c94.up.railway.app?q=Jeff`
3. Should see the answer about Jeff

### Method 2: iOS Shortcut Setup (Recommended)

**For "Get Contents of URL" Action:**
```
1. Open Shortcuts app
2. Create new shortcut
3. Add action: "Text"
   - Set to: "Shortcut Input" (spoken text)
4. Add action: "URL"
   - Set to: https://web-production-5c94.up.railway.app?q=
5. Add action: "Combine Text"
   - First: The URL
   - Second: The Text (Shortcut Input)
6. Add action: "Get Contents of URL"
   - URL: Combined Text
7. Add action: "Speak"
   - Text: Contents of URL
8. Name it and add to Siri
```

**For "Open URL" Action (Simpler):**
```
1. Open Shortcuts app
2. Create new shortcut
3. Add action: "Text"
   - Set to: "Shortcut Input"
4. Add action: "URL Encode"
   - Text: The Text from above
5. Add action: "URL"
   - Set to: https://web-production-5c94.up.railway.app?q=[Encoded Text]
6. Add action: "Open URLs"
   - Open in: Safari
7. Name it and add to Siri
```

## Deployment Options

### Option 1: Use Current Fixed Version
The main app (app_shortcut_simple.py) has been updated with fixes.

### Option 2: Switch to iOS-Optimized Version
Update your Procfile to use the iOS-optimized version:
```
web: streamlit run app_shortcut_text.py --server.port $PORT --server.address 0.0.0.0
```

### Option 3: Test Different Versions
You can test each version by updating the Procfile:
- `app_shortcut_simple.py` - Current (now fixed)
- `app_shortcut_text.py` - Pure text output
- `app_shortcut_ios.py` - Minimal HTML
- `app_shortcut_debug.py` - Full debugging

## Debugging Steps

1. **Check if query parameter is received:**
   - Visit: `https://web-production-5c94.up.railway.app?q=test`
   - Should show answer, not the regular interface

2. **Check document search:**
   - Make sure .txt files exist in `app/docs/`
   - Test with known content (e.g., "Jeff")

3. **iOS Shortcut Issues:**
   - Try "Open URLs" instead of "Get Contents of URL"
   - Check if URL encoding is needed
   - Try the pure text version (app_shortcut_text.py)

## Common Issues

1. **Blank page in Quick Look**: 
   - iOS Quick Look might not execute JavaScript
   - Solution: Use the text-only version

2. **"No information found"**:
   - Check that .txt documents exist in app/docs/
   - Verify search terms match document content

3. **Parameter not received**:
   - URL might need encoding (spaces → %20)
   - Try both ?q=test and ?q=test%20query formats

## Next Steps

1. Deploy the updated code to Railway
2. Test with the direct URL first
3. Update your iOS Shortcut to use proper URL encoding
4. Consider switching to app_shortcut_text.py for best iOS compatibility