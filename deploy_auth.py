#!/usr/bin/env python3
"""
Deploy script to switch to the authenticated Flask app
"""
import shutil
import os

print("Deploying authenticated Flask app...")

# Backup current app
if os.path.exists('app_flask.py'):
    shutil.copy('app_flask.py', 'app_flask_no_auth.py')
    print("Backed up current app to app_flask_no_auth.py")

# Copy authenticated app to main
shutil.copy('app_flask_auth.py', 'app_flask.py')
print("Deployed app_flask_auth.py as app_flask.py")

print("\nAuthentication system deployed!")
print("\nIMPORTANT:")
print("1. The default admin user is 'Jeff' with password 'changeme'")
print("2. Change the admin password immediately after first login")
print("3. Use the admin panel at /admin to add other users")
print("4. iOS shortcuts will continue to work with the user parameter")
print("\nTo rollback: copy app_flask_no_auth.py back to app_flask.py")