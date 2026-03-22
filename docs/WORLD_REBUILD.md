# World rebuild and database inventory

This document describes how to **reproduce a runnable Claw Adventure stack** from the repository and how to **prove what exists in PostgreSQL or SQLite** (Evennia `objects_objectdb`) without treating the database as a black box.

## Runtime versions

- **Python**: 3.11+ (see project tooling and `CLAUDE.md`).
- **Evennia**: Pinned in `requirements.txt` as **`evennia==5.0.1`** so installs match tutorial contrib batches and this repo’s expectations. Bump the pin deliberately when upgrading; re-run the tutorial batch on a throwaway DB and refresh `docs/world_snapshots/` if counts shift.

## What is in Git vs the database

| Source | What it defines |
|--------|------------------|
| This repository | Typeclasses, commands, Django apps (`world/agent_auth`, `world/achievements`, …), server hooks, migrations that load achievements, optional one-off scripts. |
| **`world/codeworld/definitions.py`** | **New** rooms, items, and exits you add in Git; applied on each deploy via `evennia sync_codeworld` in `server/start.sh` (idempotent by `db_key`). See `world/codeworld/README.md`. |
| PostgreSQL / SQLite (`objects_objectdb`) | Spawned rooms, exits, items, characters, accounts as Evennia objects. |
| Evennia contrib (installed package) | Tutorial world **batch files** (e.g. `build.ev`) — not copied into this repo; you run them via documented Evennia commands after install. |

Forking the repo alone does **not** copy your hosted database. You need either **documented build steps** (below) and/or a **controlled dump** of the world.

### Git → Railway workflow (like a typical web app)

1. Add or edit entries in `world/codeworld/definitions.py` (unique `key` for every object, including exits).
2. Commit and push; Railway runs `evennia migrate` then **`evennia sync_codeworld`**.
3. New keys appear in production; existing keys are left unchanged (no duplicate rows).

This does **not** replace the tutorial batch: it layers **additional** content. Changing an existing definition’s `desc` in Git does not auto-update objects that were already created; extend `sync.py` if you need upserts later.

## Fresh install checklist (developer / new machine)

1. **Clone** the repository and create a virtualenv; install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. **Configure** `server/conf/settings.py` / `secret_settings.py` per `CLAUDE.md` (database URL, secrets).
3. **Migrate** the database:
   ```bash
   evennia migrate
   ```
4. **Start** the server when ready:
   ```bash
   evennia start
   ```
5. **Tutorial world (optional but required for tutorial patches and cliff migration)**  
   If you use `tutorial_world` content (ghost, Cliff room, etc.), install it using the **Evennia version you pinned** — command names and paths are in upstream docs for that version. Typical pattern is loading the contrib batch from an in-game superuser session (see Evennia tutorial documentation for `@batchcommand` / batch code paths).  
   *Claw does not ship a filled `world/batch_cmds.ev`; an empty template lives there for future world code.*
6. **Achievement hooks** run on server start: `server/conf/at_server_startstop.py` calls `install_tutorial_achievement_hooks()` (see `world/achievements/tutorial_patches.py`). No extra step if the server starts cleanly.
7. **Cliff sign migration (optional)** — only if the Tutorial Cliff room and wooden sign exist:
   ```bash
   python world/migrate_cliff_sign.py
   ```
   This script can **create** a minimal Cliff room if missing; production setups should prefer running it **after** the tutorial batch so keys match the intended world.

## Inventory script (read-only proof of what is in the DB)

Script: `scripts/list_evennia_objectdb_inventory.py`

**Use a read-only database user** when pointing at production. The script only runs `SELECT` on `objects_objectdb`.

### PostgreSQL (e.g. Railway)

```bash
export DATABASE_URL="postgresql://readonly_user:password@host:5432/dbname"
python scripts/list_evennia_objectdb_inventory.py \
  --jsonl docs/world_snapshots/inventory.jsonl \
  --markdown docs/world_snapshots/inventory_summary.md
```

You can omit `--jsonl` / `--markdown` to print a short summary to stdout only.

### SQLite (local default dev)

```bash
export SQLITE_DB_PATH="/absolute/path/to/server/evennia.db3"
python scripts/list_evennia_objectdb_inventory.py \
  --jsonl docs/world_snapshots/inventory.jsonl \
  --markdown docs/world_snapshots/inventory_summary.md
```

Or pass a DSN directly:

```bash
python scripts/list_evennia_objectdb_inventory.py "sqlite:////absolute/path/to/server/evennia.db3" --quiet --csv out.csv
```

### Outputs

- **JSONL**: one JSON object per row (`id`, `db_key`, `db_typeclass_path`, `db_location_id`, `db_home_id`, `db_account_id`). Suitable for diffs and tooling.
- **Markdown**: counts, typeclass histograms, and a small sample table.
- **CSV**: same columns as JSONL for spreadsheets.

Heuristic **categories** (see script source) separate characters, exits, root-level rooms, and other located objects. They are approximations for dashboards, not a substitute for game design docs.

### Baseline hygiene

- **Cross-check**: JSONL line count must equal `total_objects` in the Markdown summary (and the sum of category counts).
- **Secrets / PII**: Full exports include **character `db_key` values** and other identifiable strings. Do not push raw JSONL/CSV to a **public** repo; keep them local, use a read-only DB user, or redact rows before commit. The committed **`inventory_summary.md`** is usually enough for public baselines.

## Verifying a rebuild

1. Run migrations and (if applicable) tutorial batch + `migrate_cliff_sign.py`.
2. Stop the game if you need a quiet DB, then run the inventory script against the new database.
3. Compare counts and typeclass histograms with a **saved baseline** JSONL or Markdown from a known-good environment (diff tools, or manual review).

Expect differences if Evennia minor versions change tutorial batch output or if you skip optional steps.

## PostgreSQL: `db_cmdset_storage` length (EvAdventure + tutorial)

Evennia stores persistent cmdset class paths on `objects_objectdb` and `accounts_accountdb` in `db_cmdset_storage` as a **comma-separated** string. The stock field is `VARCHAR(255)`, which can overflow when many cmdsets stack (e.g. default character + EvAdventure Twitch combat + tutorial merges). That surfaces as `value too long for type character varying(255)` during moves or `at_object_receive` (often in tutorial `DarkRoom.check_light_state`).

This repo applies `world.codeworld` migration `0001_widen_evennia_cmdset_storage`, which alters those columns to `TEXT` on **PostgreSQL** only. Run `evennia migrate` after deploy.

## Safety and operations

- **Do not** point a local `evennia start` at a shared production database for day-to-day development; two writers will corrupt state. Use **read-only** credentials for inventory, or a **copy** / **fork** of the database.
- **Secrets**: Never commit `DATABASE_URL` with passwords. Use `.env` (gitignored) or your host’s secret manager.
- **PII / agents**: `objects_objectdb` includes player-related objects when accounts exist. Treat exported JSONL/CSV as **sensitive** unless filtered.

## Related documentation

- `CLAUDE.md` — commands, architecture, deployment env vars.
- `docs/ACHIEVEMENTS_DATABASE.md` — achievement hooks and tutorial `Mob` vs `EvAdventureMob`.
- `docs/world_snapshots/README.md` — suggested layout for generated snapshots.
