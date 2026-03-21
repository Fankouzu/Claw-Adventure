# Achievements: database schema vs design doc

This document aligns the **implemented** PostgreSQL schema with the older sketch in [GAME_STATE_API_DESIGN.md](GAME_STATE_API_DESIGN.md) §3. **Implementations and frontend SQL must follow this file**, not the outdated snippets in the design doc.

## Table and model mapping

| Design doc (§3) | Implemented |
|-----------------|-------------|
| `AgentAchievement` | `UserAchievement` (`world/achievements/models.py`) |
| `db_table: agent_achievements` | **`user_achievements`** |
| `achievement_type` | **`category`** (`exploration`, `puzzle`, `story`, `combat`) |
| `requirements` (JSON) | **`requirement`** (JSON, singular) |
| Integer PK on achievements | **`id` UUID** primary key on `achievements` |
| Progress from character tags (example only) | **`exploration_progress`**, **`combat_logs`** |

## Core tables (PostgreSQL)

| Table | Purpose |
|-------|---------|
| `achievements` | Static definitions: `key` (stable string id), `name`, `description`, `category`, `points`, `is_hidden`, `icon`, `requirement` (JSONB), `created_at` |
| `user_achievements` | Unlocks: `agent_id` → `agent_auth_agents.id`, `achievement_id` → `achievements.id`, `unlocked_at` |
| `exploration_progress` | First-seen rooms per agent: `agent_id`, `room_key`, `room_name`, `visited_at` |
| `combat_logs` | Combat outcomes for stats / combat achievements: `agent_id`, `enemy_key`, `enemy_name`, `result`, `damage_*`, `combat_time` |
| `agent_auth_agents` | Agent identity (`id` UUID, `name`, …) |

Unique constraints: `(agent_id, achievement_id)` on `user_achievements`; `(agent_id, room_key)` on `exploration_progress`.

## HTTP API

The REST endpoints listed under §3.3 of the design doc are **not implemented** in this repo. Read data via **read-only SQL** (see [achievements_frontend_queries.sql](achievements_frontend_queries.sql)) or a secure BFF.

## Runtime unlock sources (server-side)

- **Exploration**: `typeclasses.characters.Character.at_post_move` → `AchievementEngine.check_exploration`.
- **Evennia tutorial_world (automatic)**: On server start, `install_tutorial_achievement_hooks()` in [`world/achievements/tutorial_patches.py`](../world/achievements/tutorial_patches.py) patches contrib `IntroRoom`, `CmdClimb`, `CmdPressButton` (crumbling wall), and `Mob` (ghost) so `cliff_explorer`, `secret_finder`, `puzzle_solver`, combat vs ghost, and `speedrunner` (first entry to `tut#16` within 5 minutes of intro) work without manual wiring. See `server/conf/at_server_startstop.py`.
- **Other games / custom content**: call `AchievementEngine.apply_context_unlock(agent, **context)` yourself; keys and values must match `requirement` JSON.
- **Combat (EvAdventure)**: `Character.at_do_loot` → `record_combat_victory_for_defeat` for `EvAdventureMob`. Optional: `typeclasses.mobs.ClawEvAdventureMob` for HP-to-zero credit (deduped with loot via `ndb`).
- **Explorer master threshold**: `AchievementEngine` reads `explorer_master.requirement.count` (default 16) when evaluating visit-all progress.

## `showmigrations` / Django checks and `AttributeProperty`

If you see `TypeError: 'NoneType' object is not callable` from `evennia.contrib.tutorials.evadventure.objects` when running `evennia showmigrations` (or any command that runs full URL checks before `evennia._init()`), the game fixes this by priming `evennia.AttributeProperty` (and related flat API) at import time in [`typeclasses/characters.py`](../typeclasses/characters.py) **before** loading evadventure. Deploy that file and retry.

## Migrations (`evennia migrate achievements`)

- **`No migrations to apply`** for `achievements` means Django has already recorded all migrations (including `0003_achievement_display_text_english`) as applied. That is **success**, not a failure.
- Verify: `evennia showmigrations achievements` — each line should show `[X]`.
- If in-game names are still non-English but `0003` is applied, rows may have been edited manually; fix with SQL `UPDATE achievements SET name=..., description=... WHERE key=...` or re-seed from `world/achievements/data.py`.

The message about **`accounts`, `comms`, `objects`, … changes not yet reflected in a migration`** comes from **Evennia core apps**, not from this project’s `world.*` apps. Do **not** run `makemigrations` on upstream Evennia packages unless you know you forked those models; it is unrelated to `achievements`.

## Frontend integration checklist

1. Use **`key`** (string) as the stable achievement identifier in UI; UUIDs are for joins only.
2. Apply **hidden** masking in the application layer: if `is_hidden` and no row in `user_achievements`, omit name/description.
3. Use a **read-only** DB role (or replica); never expose writable credentials to the browser.
