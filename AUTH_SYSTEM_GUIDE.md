# Smart Document Assistant - Authentication System Guide

## Overview
The Smart Document Assistant now includes a comprehensive user authentication system that:
- Requires users to log in before accessing the search functionality
- Automatically searches the logged-in user's folder + WMA Team folder
- Provides an admin panel for user management
- Maintains backward compatibility with iOS shortcuts

## Features

### 1. User Login System
- Secure password hashing using Werkzeug
- Session management with Flask-Login
- 7-day remember me functionality
- Automatic redirection to login for unauthorized access

### 2. User-Specific Search
- When logged in, searches automatically include:
  - The user's personal folder (weighted 2x)
  - The WMA Team folder (weighted 1x)
- No need to select user from dropdown - it uses the logged-in user

### 3. Admin Panel (`/admin`)
- Only accessible by Jeff (admin user)
- Add new users with username/password
- Optionally assign Google Drive folder IDs to users
- Delete users (except admin)
- View all users and their folder assignments

### 4. API Compatibility
- iOS shortcuts continue to work with `user` parameter
- API endpoints support both:
  - Web authentication (uses logged-in user)
  - Parameter-based authentication (for iOS shortcuts)

## Setup Instructions

### Initial Deployment

1. **Deploy the authenticated version:**
   ```bash
   python3 deploy_auth.py
   ```

2. **First Login:**
   - Username: `Jeff`
   - Password: `changeme`
   - **IMPORTANT:** Change this password immediately!

3. **Add Users:**
   - Log in as Jeff
   - Go to `/admin`
   - Add users with their usernames and passwords
   - Users already in the system will have their folder mappings preserved

### User Management

#### Adding a User:
1. Log in as Jeff
2. Navigate to `/admin`
3. Fill in:
   - Username (required)
   - Password (required)
   - Google Drive Folder ID (optional - if they have a personal folder)
4. Click "Add User"

#### Deleting a User:
1. Log in as Jeff
2. Navigate to `/admin`
3. Click "Delete" next to the user
4. Confirm the deletion

### Password Management
- Passwords are hashed using Werkzeug's secure hashing
- Users cannot change their own passwords (admin must reset)
- To reset a password: delete and re-add the user

## iOS Shortcut Configuration

iOS shortcuts will continue to work with the authentication system:

### URL Format:
```
https://your-app-url/api/search/text?q=[query]&user=[username]
```

### Example:
```
https://smart-doc-assistant.up.railway.app/api/search/text?q=What%20is%20the%20sales%20process&user=Aaron
```

The `user` parameter bypasses web authentication for API access, maintaining compatibility with existing shortcuts.

## Security Considerations

1. **Change Default Password:** The admin password 'changeme' must be changed immediately
2. **HTTPS Only:** Always use HTTPS in production
3. **Session Security:** Sessions expire after 7 days of inactivity
4. **Password Storage:** Passwords are never stored in plain text

## File Structure

- `app_flask_auth.py` - The authenticated Flask application
- `search_config.json` - Stores user data and folder mappings
- `requirements.txt` - Updated with Flask-Login and Werkzeug

## Rollback Instructions

If you need to rollback to the non-authenticated version:

```bash
cp app_flask_no_auth.py app_flask.py
```

## Troubleshooting

### Can't log in:
- Ensure the username and password are correct
- Check that the user exists in the admin panel
- Verify search_config.json has the 'users' section

### Admin panel not accessible:
- Only the 'Jeff' user can access /admin
- Ensure you're logged in as Jeff

### iOS shortcuts not working:
- Include the `user` parameter in the URL
- Ensure the user exists in the system
- Check that the API endpoint is accessible

## Environment Variables

No new environment variables are required. The system uses:
- `SECRET_KEY` - Flask session key (auto-generated if not set)
- All existing Google Drive and OpenAI variables remain the same