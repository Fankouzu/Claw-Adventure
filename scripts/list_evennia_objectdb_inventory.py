#!/usr/bin/env python3
"""
Summarize Evennia objects_objectdb: rooms, characters, exits, and other objects (items/NPCs).

Requires: pip install psycopg2-binary
Usage:
  export DATABASE_URL="postgresql://user:pass@host:port/dbname"
  python scripts/list_evennia_objectdb_inventory.py

Or pass URL as argv:
  python scripts/list_evennia_objectdb_inventory.py "postgresql://..."
"""

from __future__ import annotations

import os
import sys
import urllib.parse


def connect():
    raw = (sys.argv[1] if len(sys.argv) > 1 else os.environ.get("DATABASE_URL", "")).strip()
    if not raw:
        print("Set DATABASE_URL or pass it as the first argument.", file=sys.stderr)
        sys.exit(1)
    # sqlalchemy-style URLs are fine; strip optional +psycopg2 driver suffix if present
    if raw.startswith("postgresql+asyncpg://"):
        raw = "postgresql://" + raw.split("postgresql+asyncpg://", 1)[1]
    parsed = urllib.parse.urlparse(raw)
    if parsed.scheme not in ("postgres", "postgresql"):
        print("DATABASE_URL must be postgres / postgresql", file=sys.stderr)
        sys.exit(1)
    host = parsed.hostname or "localhost"
    port = parsed.port or 5432
    user = urllib.parse.unquote(parsed.username or "")
    password = urllib.parse.unquote(parsed.password or "")
    db = (parsed.path or "/").lstrip("/") or "postgres"
    import psycopg2

    return psycopg2.connect(
        host=host, port=port, user=user, password=password, dbname=db
    )


def main():
    conn = connect()
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM objects_objectdb")
    (total,) = cur.fetchone()
    print(f"objects_objectdb total rows: {total}\n")

    # Top-level rooms (typical): no location
    cur.execute(
        """
        SELECT COUNT(*) FROM objects_objectdb
        WHERE db_location_id IS NULL
          AND db_typeclass_path ILIKE '%room%'
          AND db_typeclass_path NOT ILIKE '%Exit%'
          AND db_typeclass_path NOT ILIKE '%Character%'
        """
    )
    (n_rooms,) = cur.fetchone()
    print(f"Likely rooms (location NULL, typeclass ~ room): {n_rooms}")

    cur.execute(
        """
        SELECT COUNT(*) FROM objects_objectdb
        WHERE db_typeclass_path ILIKE '%Exit%'
        """
    )
    (n_exits,) = cur.fetchone()
    print(f"Exits (typeclass ~ Exit): {n_exits}")

    cur.execute(
        """
        SELECT COUNT(*) FROM objects_objectdb
        WHERE db_typeclass_path ILIKE '%Character%'
        """
    )
    (n_chars,) = cur.fetchone()
    print(f"Characters (typeclass ~ Character): {n_chars}")

    # "Other" = has a container location, not Character/Exit/Account
    cur.execute(
        """
        SELECT COUNT(*) FROM objects_objectdb
        WHERE db_location_id IS NOT NULL
          AND db_typeclass_path NOT ILIKE '%Character%'
          AND db_typeclass_path NOT ILIKE '%Exit%'
          AND (db_account_id IS NULL OR db_account_id = 0)
        """
    )
    (n_other,) = cur.fetchone()
    print(
        f"Other objects with location (items, NPCs, room features, …): {n_other}\n"
    )

    print("--- Typeclass breakdown (location set, not Character/Exit) ---")
    cur.execute(
        """
        SELECT db_typeclass_path, COUNT(*) AS c
        FROM objects_objectdb
        WHERE db_location_id IS NOT NULL
          AND db_typeclass_path NOT ILIKE '%Character%'
          AND db_typeclass_path NOT ILIKE '%Exit%'
          AND (db_account_id IS NULL OR db_account_id = 0)
        GROUP BY 1
        ORDER BY c DESC, 1
        LIMIT 40
        """
    )
    for path, c in cur.fetchall():
        print(f"  {c:4d}  {path}")

    print("\n--- Sample rows (id, key, typeclass, location_id) ---")
    cur.execute(
        """
        SELECT id, db_key, db_typeclass_path, db_location_id
        FROM objects_objectdb
        WHERE db_location_id IS NOT NULL
          AND db_typeclass_path NOT ILIKE '%Character%'
          AND db_typeclass_path NOT ILIKE '%Exit%'
          AND (db_account_id IS NULL OR db_account_id = 0)
        ORDER BY id
        LIMIT 25
        """
    )
    for row in cur.fetchall():
        print(f"  id={row[0]} loc={row[3]} key={row[1]!r} type={row[2]}")

    conn.close()


if __name__ == "__main__":
    main()
