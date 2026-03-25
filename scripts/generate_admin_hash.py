"""
Run this once to generate a password hash for the admin user.
Copy the output into ADMIN_PASSWORD_HASH in .env

Usage:
    python scripts/generate_admin_hash.py
"""
import getpass
from werkzeug.security import generate_password_hash

password = getpass.getpass("Enter admin password: ")
confirm = getpass.getpass("Confirm password: ")

if password != confirm:
    print("Passwords do not match.")
else:
    print(generate_password_hash(password))
