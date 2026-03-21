"""
Migration script: Replace Cliff sign with InvitationSign

This script:
1. Finds the Cliff room (tut#02) in the Tutorial World
2. Finds the existing Wooden sign (TutorialReadable)
3. Saves the original readable_text
4. Deletes the old sign
5. Creates a new InvitationSign with the original text

Run with: python world/migrate_cliff_sign.py
"""

import os
import sys

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'server.conf.settings')
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Initialize Django
import django
django.setup()

from evennia.utils import create
from evennia.objects.models import ObjectDB


def find_or_create_cliff_room():
    """
    Find or create the Cliff room in the game world

    Returns:
        ObjectDB: The Cliff room object
    """
    # Method 1: Search by key
    cliff = ObjectDB.objects.filter(db_key__icontains="Cliff").first()

    if cliff:
        print(f"Found Cliff room: {cliff.db_key} (#{cliff.id})")
        return cliff

    # Method 2: Try to find by looking for WeatherRoom typeclass (Tutorial World)
    cliffs = ObjectDB.objects.filter(
        db_typeclass_path__contains='WeatherRoom',
        db_key__icontains='Cliff'
    )

    if cliffs.exists():
        cliff = cliffs.first()
        print(f"Found Cliff room by typeclass: {cliff.db_key} (#{cliff.id})")
        return cliff

    # Create a new Cliff room if none exists
    print("Creating new Cliff room...")
    from evennia.utils import create as create_utils

    cliff = create_utils.create_object(
        "typeclasses.rooms.Room",
        key="Cliff",
        aliases=["tut#02"]
    )
    cliff.db.desc = """You stand on a windswept cliff overlooking a vast expanse of rolling hills and distant mountains. The air is crisp and cold, carrying the scent of pine and distant rain.

A weathered wooden sign stands here, mounted on a sturdy post driven into the rocky ground."""

    print(f"Created Cliff room: {cliff.db_key} (#{cliff.id})")
    return cliff


def find_old_sign(cliff):
    """
    Find the existing Wooden sign in the Cliff room

    Args:
        cliff: The Cliff room object

    Returns:
        ObjectDB or None: The sign object
    """
    if not cliff:
        return None

    for obj in cliff.contents:
        if 'sign' in obj.db_key.lower():
            print(f"Found existing sign: {obj.db_key} (#{obj.id})")
            return obj

    return None


def migrate_cliff_sign():
    """
    Main migration function

    Replaces the existing sign with an InvitationSign, or creates a new one.
    """
    print("=" * 50)
    print("Cliff Sign Migration Script")
    print("=" * 50)

    # Find or create the Cliff room
    cliff = find_or_create_cliff_room()
    if not cliff:
        print("\nError: Could not create the Cliff room.")
        return False

    # Find the existing sign
    old_sign = find_old_sign(cliff)

    # Determine original text
    if old_sign:
        original_text = old_sign.db.readable_text or ""
        original_desc = old_sign.db.desc or ""
        original_key = old_sign.db_key or "Wooden sign"

        print(f"\nOriginal sign attributes:")
        print(f"  Key: {original_key}")
        print(f"  Readable text length: {len(original_text)} chars")

        # Delete the old sign
        print(f"\nDeleting old sign...")
        old_sign.delete()
    else:
        # Default text for new sign
        original_text = """|wBEWARE - DANGER AHEAD|n

The path beyond leads to treacherous terrain.
Many have ventured forth, few have returned.

Turn back now, or proceed at your own risk.

The choice is yours, adventurer."""
        original_desc = "A weathered wooden sign, its surface worn by countless storms."
        original_key = "Wooden sign"
        print("\nNo existing sign found. Creating new sign...")

    # Create the new InvitationSign
    print(f"Creating new InvitationSign...")

    new_sign = create.create_object(
        "typeclasses.objects.InvitationSign",
        key=original_key,
        aliases=["sign"],
        location=cliff
    )

    # Copy/set attributes
    new_sign.db.readable_text = original_text
    new_sign.db.desc = original_desc
    new_sign.locks.add("get:false()")

    print(f"\nNew sign created: {new_sign.db_key} (#{new_sign.id})")
    print(f"  Preserved original text: {len(original_text)} chars")
    print(f"  Location: {new_sign.location.db_key}")

    print("\n" + "=" * 50)
    print("Migration completed successfully!")
    print("=" * 50)

    return True


def main():
    """Main entry point"""
    try:
        success = migrate_cliff_sign()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\nError during migration: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()