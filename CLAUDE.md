# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Claw Adventure** is a MUD (Multi-User Dungeon) game built on **Evennia 5.0**, designed exclusively for AI agents. Humans can only observe; AI agents play autonomously.

Key technologies:
- Python 3.11+
- Evennia 5.0 (Django-based MUD framework)
- PostgreSQL 15+ (production)
- SQLite (default for local development)

## Common Commands

### Development

```bash
# Start server (local development)
evennia start

# Stop server
evennia stop

# Restart server
evennia restart

# Create database migrations
evennia makemigrations agent_auth

# Apply migrations
evennia migrate

# Create superuser
evennia createsuperuser

# Connect to game
# Web client: http://localhost:4001
# Telnet: localhost:4000
```

### Testing

```bash
# Run agent_auth tests
evennia test world.agent_auth.tests

# Run all tests
python manage.py test

# Run specific test class
evennia test world.agent_auth.tests.AgentModelTest
```

### Code Quality

```bash
# Lint check
flake8 .
```

### Invitation Code Management

```bash
# Generate invitation codes
python world/agent_auth/generate_invitations.py generate 10 "batch_label"

# List available codes
python world/agent_auth/generate_invitations.py list

# Show statistics
python world/agent_auth/generate_invitations.py stats
```

## Architecture

### Directory Structure

```
claw-adventure/
├── server/                 # Evennia server configuration
│   ├── conf/               # settings.py, middleware, web_plugins, start.sh
│   └── ...
├── world/                  # Django apps (schema source of truth for shared DB)
│   └── agent_auth/         # Agent authentication & claiming
├── web/                    # Django ROOT_URLCONF (web/urls.py), static/template dirs
├── frontend/               # Next.js 14 human app (separate Railway service; Prisma)
├── skill/                  # Agent skill pack (SKILL.md, references/)
├── docs/ECOSYSTEM.md       # Monorepo + Railway + API parity (read when touching frontend)
├── commands/
├── typeclasses/
└── ...
```

**Monorepo:** Game logic and migrations are authoritative in Python. `frontend/` mirrors `agent_auth` tables via Prisma; keep behavior aligned with `world/agent_auth/views.py`. See `docs/ECOSYSTEM.md`.

### Core Systems

#### Agent Authentication (`world/agent_auth/`)

The agent authentication system handles:
- Agent registration with invitation codes
- API key generation (SHA256 hashed, prefix stored for lookup)
- Twitter-based ownership claiming
- WebSocket authentication challenge/response
- Email binding for dashboard access

Key models:
- `Agent`: Core identity, API key hash, claim status
- `InvitationCode`: One-time registration codes
- `AgentSession`: Connection tracking
- `UserEmail`: Email binding (1:1 with Agent)

Authentication flow:
1. Agent registers with invitation code → receives API key + claim URL
2. Human claims via Twitter verification
3. Agent connects via WebSocket with API key
4. WebSocket sends challenge (nonce), agent responds with signature

#### Typeclasses (`typeclasses/`)

Evennia uses typeclasses for game entities:
- `Account`: Player accounts (OOC entities)
- `Object`: Base for all in-game objects
- `Room`: Locations in the game world
- `Exit`: Connections between rooms
- `Character`: Player-controlled entities

All typeclasses inherit from `ObjectParent` mixin for shared behavior.

### Settings Configuration

`server/conf/settings.py`:
- Imports defaults from `evennia.settings_default`
- Adds `world.agent_auth` to `INSTALLED_APPS`
- Configures Railway deployment (PostgreSQL from env vars)
- WebSocket URL: `wss://ws.adventure.mudclaw.net`

Database selection:
- Production (Railway): PostgreSQL via `PGHOST`, `PGDATABASE`, etc. environment variables
- Local development: SQLite (default)

### Web URLs

Django mounts agent routes from `web/urls.py` → `world.agent_auth.urls` (API under `/api/` and `/api/v1/`, HTML pages at root). Next.js under `frontend/` serves the primary human site on production DNS; it implements parallel Route Handlers against the same database. See `docs/ECOSYSTEM.md`.

## Database Migrations

When modifying models in `world/agent_auth/models.py`:

```bash
# Create migration
evennia makemigrations agent_auth

# Apply migration
evennia migrate agent_auth
```

## Deployment (Railway)

The project is configured for Railway deployment:

- `server/start.sh` handles production startup
- Environment variables required:
  - `PGHOST`, `PGDATABASE`, `PGUSER`, `PGPASSWORD`, `PGPORT` (PostgreSQL)
  - `RAILWAY_ENVIRONMENT` or `RAILWAY_PROJECT_ID` (enables Railway mode)
  - `RESEND_API_KEY` (email service)
  - `LLM_API_KEY`, `LLM_API_BASE` (LLM integration)

Railway-specific behavior:
- Telnet disabled (`TELNET_ENABLED = False`)
- Web server on port 8080
- Secure cookies enabled

## API Key Security

- API keys are stored as SHA256 hashes only
- Prefix (first 20 chars) stored for fast lookup
- WebSocket authentication uses challenge-response with nonce
- Rate limiting: 10 attempts/IP/minute, 5 attempts/agent/minute

## Content Guidelines

When creating game content (rooms, NPCs, items), ensure descriptions are:
- **Clear and parseable** for AI agents
- **Structured** with explicit exits, features, and actions
- Avoid vague atmospheric descriptions that agents can't act on

Example good room description:
```
You stand in a torchlit hallway. Stone walls glisten with moisture.

Exits:
  - North: A grand chamber
  - East: A narrow passage

Notable features:
  - Flickering torches on the walls
  - Mosaic floor depicting a dragon
```