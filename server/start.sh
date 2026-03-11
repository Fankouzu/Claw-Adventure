#!/bin/bash

echo "========================================"
echo "[STARTUP] Initializing Evennia..."
echo "========================================"

# Run migrations
echo "[STARTUP] Running database migrations..."
evennia migrate || echo "[STARTUP] Migrate completed with warnings"

# Create superuser if not exists
echo "[STARTUP] Checking/Creating superuser..."

# Use a Python one-liner that's more robust
python -c "
import os
import sys
import django

# Set the correct settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'server.conf.settings')

try:
    django.setup()
    
    from evennia.accounts.models import AccountDB
    from evennia.accounts.accounts import DefaultAccount
    
    username = os.environ.get('EVENNIA_SUPERUSER_NAME', 'admin')
    password = os.environ.get('EVENNIA_SUPERUSER_PASSWORD', 'admin123')
    email = os.environ.get('EVENNIA_SUPERUSER_EMAIL', 'admin@localhost')
    
    existing = AccountDB.objects.filter(username=username).first()
    if existing:
        print(f'[STARTUP] Superuser \"{username}\" already exists (id={existing.id})')
    else:
        account = AccountDB.objects.create_account(
            username=username,
            email=email,
            password=password,
            typeclass=DefaultAccount
        )
        account.permissions.add('Developer')
        account.permissions.add('Admin')
        print(f'[STARTUP] Superuser \"{username}\" created successfully (id={account.id})')
except Exception as e:
    print(f'[STARTUP] Error creating superuser: {e}')
    import traceback
    traceback.print_exc()
" 2>&1

echo "[STARTUP] Starting Evennia server..."
exec evennia start -l