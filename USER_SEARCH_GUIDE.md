# User-Specific Search Guide

## Overview
The Smart Document Assistant now supports user-specific folder searching. When a user is specified, the system will prioritize searching their personal folder before searching the general WMA Team folder.

## User Folder Mappings
The following users have dedicated folders configured:
- Aaron
- Brody
- Dona
- Eric
- Grace
- Jeff
- Jessica
- Jill
- John
- Jon
- Kirk
- Owen
- Paul

## How It Works

### Search Priority
1. **User Folder First**: If a user is specified, their folder is searched first with a weight of 2.0
2. **Team Folder Second**: The WMA Team folder is searched next with a weight of 1.0
3. **Result Ordering**: Results from user folders appear first in the AI summary

### API Endpoints

#### Search with User Context
```
GET /api/search?q=<query>&user=<username>
GET /api/search/text?q=<query>&user=<username>
```

#### Get Available Users
```
GET /api/users
```
Returns a JSON list of available users.

### iOS Shortcuts Integration
The iOS endpoints (`/api/search` and `/api/search/text`) now accept an optional `user` parameter. When the Shortcuts app identifies the user, pass their name to get personalized results.

### Web Interface
The web interface at `/` now includes a dropdown to select a user for personalized searches.

## Configuration
User folder mappings are stored in `search_config.json`. The configuration includes:
- `user_folders`: Mapping of usernames to Google Drive folder IDs
- `default_team_folder`: The WMA Team folder ID
- `search_weights`: Weights for prioritizing results (user folder: 2.0, team folder: 1.0)