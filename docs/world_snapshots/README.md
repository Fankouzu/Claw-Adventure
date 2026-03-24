<!-- doc: world_snapshots/README.md | audience: builders | lang: en -->

# World snapshots (generated)

This directory is the **recommended location** for outputs from
`scripts/list_evennia_objectdb_inventory.py` (JSONL, Markdown, CSV).

## Usage

From the repository root:

```bash
export DATABASE_URL="postgresql://..."
python scripts/list_evennia_objectdb_inventory.py \
  --jsonl docs/world_snapshots/inventory.jsonl \
  --markdown docs/world_snapshots/inventory_summary.md
```

See `docs/world-rebuild.md` for full context.

## Git policy

- **Optional**: Commit a **baseline** `inventory_summary.md` (low sensitivity) to track world shape over time.
- **Avoid** committing JSONL/CSV to **public** remotes: they include **character keys** (`db_key`) and other identifiable fields. This repo gitignores `*.jsonl` / `*.csv` here by default; remove from the index with `git rm --cached` if they were added before that rule.
- Add specific filenames to `.gitignore` if you prefer to keep all snapshots local only.

## Naming suggestion

- `inventory_YYYYMMDD.jsonl` / `inventory_YYYYMMDD_summary.md` for dated baselines.
