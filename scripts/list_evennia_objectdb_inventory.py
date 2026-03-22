#!/usr/bin/env python3
"""
Summarize and export Evennia ``objects_objectdb`` rows for auditing and rebuild verification.

Supports:
  - PostgreSQL via ``DATABASE_URL`` (``postgresql://...``) or positional DSN
  - SQLite via ``sqlite:///relative/or/absolute/path.db3``

Outputs (optional):
  - JSONL: one JSON object per line (full row snapshot)
  - Markdown: human-readable counts and typeclass breakdown

Requires PostgreSQL: ``pip install psycopg2-binary`` (already in project requirements).
SQLite uses the standard library only.

Examples:
  export DATABASE_URL="postgresql://user:pass@host:5432/dbname"
  python scripts/list_evennia_objectdb_inventory.py

  python scripts/list_evennia_objectdb_inventory.py \\
    --jsonl docs/world_snapshots/inventory.jsonl \\
    --markdown docs/world_snapshots/inventory_summary.md

  python scripts/list_evennia_objectdb_inventory.py "sqlite:////path/to/server/evennia.db3"
"""

from __future__ import annotations

import argparse
import csv
import io
import json
import os
import sys
import urllib.parse
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _resolve_dsn(args: argparse.Namespace) -> str:
    if args.dsn:
        return args.dsn.strip()
    env = os.environ.get("DATABASE_URL", "").strip()
    if env:
        return env
    sqlite_path = os.environ.get("SQLITE_DB_PATH", "").strip()
    if sqlite_path:
        p = Path(sqlite_path).expanduser().resolve()
        return f"sqlite:///{p.as_posix()}"
    print(
        "Provide a DSN as the first argument, or set DATABASE_URL or SQLITE_DB_PATH.",
        file=sys.stderr,
    )
    sys.exit(1)


def _connect(dsn: str):
    """Return (connection, dialect) where dialect is 'postgres' or 'sqlite'."""
    dsn = dsn.strip()
    if dsn.startswith("postgresql+asyncpg://"):
        dsn = "postgresql://" + dsn.split("postgresql+asyncpg://", 1)[1]
    parsed = urllib.parse.urlparse(dsn)
    scheme = (parsed.scheme or "").lower()

    if scheme in ("postgres", "postgresql"):
        import psycopg2

        host = parsed.hostname or "localhost"
        port = parsed.port or 5432
        user = urllib.parse.unquote(parsed.username or "")
        password = urllib.parse.unquote(parsed.password or "")
        db = (parsed.path or "/").lstrip("/") or "postgres"
        conn = psycopg2.connect(
            host=host, port=port, user=user, password=password, dbname=db
        )
        return conn, "postgres"

    if scheme == "sqlite":
        # Prefer sqlite:///path after the scheme (avoids urlparse eating relative paths).
        lower = dsn.lower()
        if not lower.startswith("sqlite:///"):
            print(
                "SQLite DSN must look like sqlite:///path/to/file.db3 "
                "(three slashes; use an absolute path if unsure).",
                file=sys.stderr,
            )
            sys.exit(1)
        raw_path = urllib.parse.unquote(dsn.split("sqlite:///", 1)[1])
        path = Path(raw_path).expanduser().resolve()
        import sqlite3

        conn = sqlite3.connect(str(path))
        conn.row_factory = sqlite3.Row
        return conn, "sqlite"

    print(
        "DSN must be postgresql://... or sqlite:///path (see script docstring).",
        file=sys.stderr,
    )
    sys.exit(1)


def _fetch_all_rows(conn, dialect: str) -> list[dict[str, Any]]:
    sql = """
        SELECT id, db_key, db_typeclass_path, db_location_id, db_home_id, db_account_id
        FROM objects_objectdb
        ORDER BY id
    """
    cur = conn.cursor()
    cur.execute(sql)
    columns = [d[0] for d in cur.description]
    rows: list[dict[str, Any]] = []
    for tup in cur.fetchall():
        if dialect == "sqlite":
            row = dict(tup)
        else:
            row = dict(zip(columns, tup))
        # Normalize for JSON (some drivers return Decimal etc.)
        for k, v in list(row.items()):
            if hasattr(v, "isoformat"):
                row[k] = v.isoformat()
            elif isinstance(v, memoryview):
                row[k] = v.tobytes().decode("utf-8", errors="replace")
        rows.append(row)
    cur.close()
    return rows


def _classify(row: dict[str, Any]) -> str:
    """
    Approximate categories aligned with the original SQL summaries.
    Order matters: Character and Exit before generic room/other.
    """
    tc = (row.get("db_typeclass_path") or "") or ""
    tl = tc.lower()
    loc = row.get("db_location_id")
    acct = row.get("db_account_id")

    if "character" in tl:
        return "character"
    if "exit" in tl:
        return "exit"
    if loc is None and "room" in tl:
        return "root_room"
    if acct is not None and acct not in (0, None):
        # Puppet / account-bound objects (often Characters already matched)
        return "account_bound"
    if loc is not None and "character" not in tl and "exit" not in tl:
        return "located_other"
    return "other"


def _summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
    by_cat = Counter(_classify(r) for r in rows)
    type_counts = Counter((r.get("db_typeclass_path") or "") for r in rows)
    return {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "total_objects": len(rows),
        "by_category": dict(by_cat),
        "typeclass_counts": dict(type_counts.most_common()),
    }


def _write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def _write_markdown(path: Path, rows: list[dict[str, Any]], summary: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    by_tc = Counter((r.get("db_typeclass_path") or "") for r in rows)
    located_other = [
        r
        for r in rows
        if _classify(r) == "located_other"
    ]
    loc_tc = Counter((r.get("db_typeclass_path") or "") for r in located_other)

    lines = [
        "# Evennia ObjectDB inventory summary",
        "",
        f"- Generated (UTC): `{summary['generated_at_utc']}`",
        f"- Total rows: **{summary['total_objects']}**",
        "",
        "## Counts by heuristic category",
        "",
        "| Category | Count |",
        "|----------|-------|",
    ]
    for cat in sorted(summary["by_category"], key=lambda c: -summary["by_category"][c]):
        lines.append(f"| `{cat}` | {summary['by_category'][cat]} |")
    lines.extend(
        [
            "",
            "## Top typeclasses (all objects)",
            "",
            "| Count | Typeclass |",
            "|------:|-----------|",
        ]
    )
    for tc, c in by_tc.most_common(50):
        safe = tc.replace("|", "\\|") if tc else "(empty)"
        lines.append(f"| {c} | `{safe}` |")

    lines.extend(
        [
            "",
            "## Top typeclasses (located non-character, non-exit)",
            "",
            "| Count | Typeclass |",
            "|------:|-----------|",
        ]
    )
    for tc, c in loc_tc.most_common(40):
        safe = tc.replace("|", "\\|") if tc else "(empty)"
        lines.append(f"| {c} | `{safe}` |")

    lines.extend(
        [
            "",
            "## Sample located objects (first 40 by id)",
            "",
            "| id | db_key | typeclass | location_id |",
            "|---:|--------|-----------|------------:|",
        ]
    )
    samples = sorted(located_other, key=lambda r: r.get("id") or 0)[:40]
    for r in samples:
        kid = r.get("id")
        key = (r.get("db_key") or "").replace("|", "\\|")
        tc = (r.get("db_typeclass_path") or "").replace("|", "\\|")
        lid = r.get("db_location_id")
        lines.append(f"| {kid} | {key} | `{tc}` | {lid} |")

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _print_stdout(summary: dict[str, Any], rows: list[dict[str, Any]]) -> None:
    print(f"objects_objectdb total rows: {summary['total_objects']}\n")
    print("--- By heuristic category ---")
    for cat in sorted(summary["by_category"], key=lambda c: -summary["by_category"][c]):
        print(f"  {summary['by_category'][cat]:5d}  {cat}")
    print("\n--- Top 25 typeclasses (all objects) ---")
    tc = Counter((r.get("db_typeclass_path") or "") for r in rows)
    for name, c in tc.most_common(25):
        display = name or "(empty)"
        print(f"  {c:5d}  {display}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Export Evennia ObjectDB inventory for auditing."
    )
    parser.add_argument(
        "dsn",
        nargs="?",
        default=None,
        help="postgresql://... or sqlite:///path (else DATABASE_URL / SQLITE_DB_PATH)",
    )
    parser.add_argument(
        "--jsonl",
        type=Path,
        default=None,
        help="Write full table snapshot as JSONL",
    )
    parser.add_argument(
        "--markdown",
        type=Path,
        default=None,
        help="Write Markdown summary",
    )
    parser.add_argument(
        "--csv",
        type=Path,
        default=None,
        help="Write full table snapshot as CSV",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Do not print summary to stdout (still writes output files)",
    )
    args = parser.parse_args()
    dsn = _resolve_dsn(args)

    conn, dialect = _connect(dsn)
    try:
        rows = _fetch_all_rows(conn, dialect)
    finally:
        conn.close()

    summary = _summarize(rows)

    if args.jsonl:
        _write_jsonl(args.jsonl, rows)
        print(f"Wrote JSONL: {args.jsonl}", file=sys.stderr)
    if args.markdown:
        _write_markdown(args.markdown, rows, summary)
        print(f"Wrote Markdown: {args.markdown}", file=sys.stderr)
    if args.csv:
        args.csv.parent.mkdir(parents=True, exist_ok=True)
        buf = io.StringIO()
        if rows:
            w = csv.DictWriter(buf, fieldnames=list(rows[0].keys()))
            w.writeheader()
            w.writerows(rows)
        args.csv.write_text(buf.getvalue(), encoding="utf-8")
        print(f"Wrote CSV: {args.csv}", file=sys.stderr)

    if not args.quiet:
        _print_stdout(summary, rows)


if __name__ == "__main__":
    main()
