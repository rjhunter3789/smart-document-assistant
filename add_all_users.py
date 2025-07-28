#!/usr/bin/env python3
"""
Add all team members to the system with their folder mappings
"""
from werkzeug.security import generate_password_hash
import json

# Team members and their folder IDs
team_members = {
    'aaron': '10xz-BlLy2UUs6VzXftM0-qi-pd86_JG2',
    'brody': '1ark3Az_F8aRr5N9OfldiBxEbH8Lo2c8d',
    'dona': '1dUTYf82QkOV4Tt1d9dtO115paJxdUY99',
    'eric': '1A7UP4GZKnEcZqYu-dlXXuWdnw9QHzSo2',
    'grace': '1T7CnMHV5lW4SRvpmwMt_g6W_BtxPBi6l',
    'jeff': '1M0mNJHCuXCqURzazJ1FJA1BtLpYhJ50j',
    'jessica': '1KRAfY4Kj2Vu-u9TAKbV1tylI92IrevkP',
    'jill': '1uYkUUZIIpeTzxFEO7nAjlsxrfJ0hSX-D',
    'john': '17LV5meOJJtoEX5H-NPVYtOCPvL9Iq3LC',
    'jon': '1Wgm-a_tauNw48JREqieiaGUXPSWVsO8C',
    'kirk': '1vDs-ED2itiSEYpKauIk3IfBzNytLvtrl',
    'owen': '111_VwWezw-tmZkCeM9islngsJfHGgIhL',
    'paul': '1hpnnKge4Sna_TOU0hOjxk8uzEwGOynsZ'
}

# Load existing config
try:
    with open('search_config.json', 'r') as f:
        config = json.load(f)
except:
    config = {
        'user_folders': {},
        'users': {},
        'default_team_folder': '1INF091UIAoK87SIVzN4MpeUERyAyO-w4',
        'search_weights': {'user_folder': 2.0, 'team_folder': 1.0}
    }

# Ensure required sections exist
if 'users' not in config:
    config['users'] = {}
if 'user_folders' not in config:
    config['user_folders'] = {}

# Add all team members
print("Adding team members...")
passwords = {}

for username, folder_id in team_members.items():
    # Generate default password (username + 123)
    password = f"{username}123"
    passwords[username] = password
    
    # Add user with hashed password (only if not exists)
    if username not in config['users']:
        config['users'][username] = {
            'password': generate_password_hash(password)
        }
        print(f"✓ Added user: {username}")
    else:
        print(f"- User {username} already exists")
    
    # Add folder mapping
    config['user_folders'][username] = folder_id

# Also add WMA Team folder
config['user_folders']['WMA Team'] = '1INF091UIAoK87SIVzN4MpeUERyAyO-w4'

# Save config
with open('search_config.json', 'w') as f:
    json.dump(config, f, indent=2)

print("\n✅ All team members added successfully!")
print("\n📋 User Credentials:")
print("-" * 40)
for username, password in sorted(passwords.items()):
    print(f"{username:10} : {password}")
print("-" * 40)
print("\n⚠️  IMPORTANT: These are temporary passwords!")
print("Users should change them after first login.")
print("\n🔗 iOS Shortcut URLs:")
print("-" * 60)
for username in sorted(team_members.keys()):
    print(f"{username}: &user={username}")
print("-" * 60)