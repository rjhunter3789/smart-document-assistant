#!/usr/bin/env python3
"""
Migration script to add all existing users with default passwords
This should be run on the server after deploying the authenticated app
"""

def generate_migration_code():
    """Generate Python code to add all users"""
    
    users = [
        'Aaron', 'Brody', 'Dona', 'Eric', 'Grace', 'Jeff',
        'Jessica', 'Jill', 'John', 'Jon', 'Kirk', 'Owen', 'Paul'
    ]
    
    print("# Run this code in Python on the server after deploying app_flask_auth.py")
    print("# It will add all users with default passwords\n")
    
    print("from werkzeug.security import generate_password_hash")
    print("import json\n")
    
    print("# Load config")
    print("with open('search_config.json', 'r') as f:")
    print("    config = json.load(f)\n")
    
    print("# Add all users with default passwords")
    print("if 'users' not in config:")
    print("    config['users'] = {}\n")
    
    print("users_to_add = {")
    for user in users:
        password = f"{user.lower()}123"
        print(f"    '{user}': generate_password_hash('{password}'),")
    print("}\n")
    
    print("# Update config with users")
    print("for username, password_hash in users_to_add.items():")
    print("    config['users'][username] = {'password': password_hash}\n")
    
    print("# Save config")
    print("with open('search_config.json', 'w') as f:")
    print("    json.dump(config, f, indent=2)\n")
    
    print("print('All users added successfully!')")
    print("print('\\nDefault passwords:')")
    print("for user in users_to_add:")
    print("    print(f'  {user}: {user.lower()}123')")
    print("print('\\nIMPORTANT: Users should change their passwords!')")

if __name__ == "__main__":
    print("MIGRATION INSTRUCTIONS")
    print("=" * 50)
    print("\n1. Deploy the authenticated app:")
    print("   python3 deploy_auth.py\n")
    print("2. Run the following code on your server:\n")
    print("-" * 50)
    generate_migration_code()
    print("-" * 50)
    print("\n3. All users will be able to log in with their default passwords")
    print("4. Jeff can manage users through the /admin panel")