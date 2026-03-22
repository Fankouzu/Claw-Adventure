# CLAUDE.md — `frontend/` (Next.js)

## Monorepo context

This directory is **`frontend/`** inside **claw-adventure**. The **Evennia game and Django models** live at the repository root (`world/`, `server/`). **Canonical behavior** for agent registration, invitation/fission logic, and DB schema is **`world/agent_auth/views.py`** and Django migrations.

Read **[docs/ECOSYSTEM.md](../docs/ECOSYSTEM.md)** before changing Prisma or API routes.

## Production URLs

- **Human site / browser APIs (typical):** `https://mudclaw.net` (this Next app)
- **WebSocket (agents):** `wss://ws.adventure.mudclaw.net` (Evennia; not Next.js)

## Stack

- Next.js 14 (App Router), TypeScript, Tailwind, next-intl
- Prisma 7 + PostgreSQL (**same `DATABASE_URL` as backend** in production)
- iron-session, Resend (optional)

## Layout

- `app/[locale]/` — localized pages
- `app/api/` — Route Handlers (Prisma); keep **parity** with `world/agent_auth` for shared flows (e.g. `register` → `fission_code`, `message`, `InvitationRelationship`)
- `lib/db.ts`, `lib/crypto.ts` — Prisma client; `generateId()` must be **UUID** (Django `Agent.id`)
- `prisma/schema.prisma` — `@@map` to `agent_auth_*` tables; extend when Django adds columns
- **Agent `level` / `experience`:** backend rule is **`level = experience // 100 + 1`** after internal `POST .../experience` (`world/agent_auth/views.py`); in-MUD character stats differ — [docs/ECOSYSTEM.md](../docs/ECOSYSTEM.md)

## Commands

```bash
npm run dev
npm run build
npm run lint
npx prisma generate
```

## Env

`DATABASE_URL`, `SESSION_SECRET`, `NEXT_PUBLIC_BASE_URL`, optional `RESEND_*`

## Language

- User-facing assistant replies: Chinese (per project preference)
- Code comments: English
- Commits: English
