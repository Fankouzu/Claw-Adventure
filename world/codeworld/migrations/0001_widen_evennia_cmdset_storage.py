"""
Evennia stores persistent cmdset import paths in db_cmdset_storage as comma-separated
strings. The model field is CharField(max_length=255), which is too small when many
cmdsets stack (EvAdventure + Twitch combat + tutorial + account merge).

Symptom: PostgreSQL raises "value too long for type character varying(255)" during
room at_object_receive (e.g. DarkRoom.check_light_state saving the room) or character moves.

This migration widens the column at the database level only; Evennia's ORM definition
unchanged (upstream fix would be TextField in a future Evennia release).
"""

from django.db import migrations


def _widen_postgresql(apps, schema_editor):
    if schema_editor.connection.vendor != "postgresql":
        return
    # Table names follow Django defaults for Evennia apps.
    with schema_editor.connection.cursor() as cursor:
        cursor.execute(
            """
            ALTER TABLE objects_objectdb
            ALTER COLUMN db_cmdset_storage TYPE TEXT
            USING db_cmdset_storage::TEXT;
            """
        )
        cursor.execute(
            """
            ALTER TABLE accounts_accountdb
            ALTER COLUMN db_cmdset_storage TYPE TEXT
            USING db_cmdset_storage::TEXT;
            """
        )


def _noop_reverse(apps, schema_editor):
    # Do not shrink columns; data may already exceed 255 characters.
    pass


class Migration(migrations.Migration):
    dependencies = [
        (
            "objects",
            "0013_defaultobject_alter_objectdb_id_defaultcharacter_and_more",
        ),
        ("accounts", "0012_defaultaccount_alter_accountdb_id_account_bot_and_more"),
    ]

    operations = [
        migrations.RunPython(_widen_postgresql, _noop_reverse),
    ]
