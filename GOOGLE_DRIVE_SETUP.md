# Google Drive Setup Guide

## Prerequisites
1. Google Cloud Console access
2. Google Drive with documents to search

## Step 1: Enable Google Drive API

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a new project or select existing
3. Enable the Google Drive API:
   - Go to "APIs & Services" > "Library"
   - Search for "Google Drive API"
   - Click and enable it

## Step 2: Create OAuth 2.0 Credentials

1. Go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "OAuth client ID"
3. Choose "Web application"
4. Add authorized redirect URIs:
   - `http://localhost:8080`
   - `https://developers.google.com/oauthplayground`
5. Save the client ID and client secret

## Step 3: Get Refresh Token

1. Go to [OAuth Playground](https://developers.google.com/oauthplayground)
2. Click the gear icon (top right) > "Use your own OAuth credentials"
3. Enter your client ID and client secret
4. In the left panel, find and select:
   - `https://www.googleapis.com/auth/drive.readonly`
5. Click "Authorize APIs" and grant permissions
6. Click "Exchange authorization code for tokens"
7. Copy the refresh token

## Step 4: Configure Railway Environment Variables

Add these to your Railway project:

```bash
GOOGLE_CLIENT_ID=your_client_id_here
GOOGLE_CLIENT_SECRET=your_client_secret_here
GOOGLE_REFRESH_TOKEN=your_refresh_token_here
GOOGLE_TOKEN=your_access_token_here
```

## Step 5: Alternative - Local credentials.json

Create a `credentials.json` file:

```json
{
    "client_id": "your_client_id_here",
    "client_secret": "your_client_secret_here",
    "refresh_token": "your_refresh_token_here",
    "token": "your_access_token_here",
    "token_uri": "https://oauth2.googleapis.com/token",
    "type": "authorized_user"
}
```

**Note**: Don't commit this file to Git! Add to .gitignore.

## Step 6: Update Folder ID

In `app_flask_drive.py`, update the `PARENT_FOLDER_ID`:

1. Open Google Drive
2. Navigate to your documents folder
3. Copy the folder ID from the URL:
   - URL: `https://drive.google.com/drive/folders/FOLDER_ID_HERE`
4. Replace in code:
   ```python
   PARENT_FOLDER_ID = "your_folder_id_here"
   ```

## Testing

1. Check connection status:
   ```
   https://your-app.railway.app/api/status
   ```

2. Test search:
   ```
   https://your-app.railway.app/api/search/text?q=test
   ```

## Troubleshooting

- **"Credentials missing"**: Environment variables not set
- **"Authentication failed"**: Token expired or invalid
- **No Drive results**: Check folder ID and permissions
- **403 errors**: Scope insufficient - needs drive.readonly