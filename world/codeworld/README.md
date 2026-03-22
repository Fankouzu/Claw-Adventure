# Code-defined world (`world.codeworld`)

This package supports a **web-style workflow**: edit Python data in Git, push, deploy, and the server materializes new rooms/items/exits in PostgreSQL **without** using `@create` / `@dig` in production.

## How it works

1. **`definitions.py`** — lists `CODED_ROOMS`, `CODED_THINGS`, and `CODED_EXITS` (see examples in comments).
2. **`sync.py`** — for each entry, creates the object **only if** no `ObjectDB` row with the same `db_key` exists yet.
3. **`evennia sync_codeworld`** — invoked from **`server/start.sh`** after migrations on Railway (and can be run locally).

## Rules

- **Globally unique `key`** for every definition (including exits). Evennia object keys should not collide with tutorial content; use a prefix such as `Claw / …`.
- **Order**: all rooms first, then things (need `location_key`), then exits (need both room keys to exist). Linking to the stock **Limbo** room is fine if you use `destination_key: "Limbo"` (exact `db_key`).
- **Updates**: changing `desc` in Git does **not** overwrite an existing object; only missing keys are created. To refresh text, extend sync logic later or edit once in-game.
- **Tag**: created objects get tag `claw_codeworld` (category `world`) for filtering and audits.

## Relation to the tutorial world

Tutorial rooms live in the DB from Evennia’s batch, not from this file. You can still attach **new** Claw-prefixed rooms or exits that point into tutorial rooms by using their exact `db_key` strings (verify with `scripts/list_evennia_objectdb_inventory.py`).

## Local test

```bash
evennia sync_codeworld
```

Empty lists are a no-op (created=0).
