#!/bin/bash

echo "========================================"
echo "[STARTUP] Initializing Evennia..."
echo "========================================"

# Set environment for Django
export DJANGO_SETTINGS_MODULE=server.conf.settings

# Run migrations (skip interactive superuser creation)
echo "[STARTUP] Running database migrations..."
evennia migrate --noinput 2>&1 || evennia migrate 2>&1

# Create superuser using Django's environment variable method
echo "[STARTUP] Checking/Creating superuser..."

# Set the password via environment variable for Django's createsuperuser --noinput
export DJANGO_SUPERUSER_PASSWORD="${EVENNIA_SUPERUSER_PASSWORD:-admin123}"

# Use Django's management command directly
python -c "
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'server.conf.settings')
django.setup()

from django.contrib.auth import get_user_model
from evennia.accounts.models import AccountDB
from evennia.accounts.accounts import DefaultAccount

User = get_user_model()
username = os.environ.get('EVENNIA_SUPERUSER_NAME', 'admin')
password = os.environ.get('EVENNIA_SUPERUSER_PASSWORD', 'admin123')
email = os.environ.get('EVENNIA_SUPERUSER_EMAIL', 'admin@localhost')

# Check if user exists
if User.objects.filter(username=username).exists():
    print(f'[STARTUP] User \"{username}\" already exists')
else:
    # Create Django superuser
    user = User.objects.create_superuser(username=username, email=email, password=password)
    print(f'[STARTUP] Django superuser \"{username}\" created')

# Also create Evennia Account if needed
if not AccountDB.objects.filter(username=username).exists():
    account = AccountDB.objects.create_account(
        username=username,
        email=email,
        password=password,
        typeclass=DefaultAccount
    )
    account.permissions.add('Developer')
    account.permissions.add('Admin')
    print(f'[STARTUP] Evennia account \"{username}\" created with Developer/Admin permissions')
else:
    print(f'[STARTUP] Evennia account \"{username}\" already exists')
" 2>&1

echo "[STARTUP] Starting Evennia server..."
exec evennia start -l