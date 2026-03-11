#!/bin/bash
set -e

echo "Running migrations..."
evennia migrate

echo "Checking/Creating superuser..."
python << 'EOF'
import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.conf.settings")
django.setup()

from evennia.accounts.models import AccountDB
from evennia.accounts.accounts import DefaultAccount

username = os.environ.get("EVENNIA_SUPERUSER_NAME", "admin")
password = os.environ.get("EVENNIA_SUPERUSER_PASSWORD", "admin123")
email = os.environ.get("EVENNIA_SUPERUSER_EMAIL", "admin@localhost")

if not AccountDB.objects.filter(username=username).exists():
    account = AccountDB.objects.create_account(
        username=username,
        email=email,
        password=password,
        typeclass=DefaultAccount
    )
    account.permissions.add("Developer")
    account.permissions.add("Admin")
    print(f"[startup] Superuser '{username}' created successfully!")
else:
    print(f"[startup] Superuser '{username}' already exists.")
EOF

echo "Starting Evennia..."
exec evennia start -l