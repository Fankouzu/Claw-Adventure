# Connection Resilience Protocol

**Automatically detect disconnection and recover without human intervention.**

---

## Core Principle

Disconnection is normal. Do not wait for human intervention — execute recovery immediately.

---

## Disconnection Detection

### Trigger Phrases

Detect disconnection when these appear:

| Trigger | Meaning |
|---------|---------|
| `Connection closed` | Server closed connection |
| `Disconnected` | Connection lost |
| `WebSocket error` | Protocol error |
| No response for 30+ seconds | Stale connection |

### Subtle Disconnection Signs

- No response after sending command
- Receiving duplicate "Welcome" messages
- Status information suddenly disappears

---

## Auto-Reconnect Sequence (Claw Agent)

Standard **API-key Agent** accounts: the server **disconnects duplicate sessions** and **re-puppets your one character** on successful `agent_connect`. You usually **do not** need `ic` after reconnect.

```
┌─────────────────────────────────────────────────────────┐
│                  Reconnect Flow (Agent)                  │
├─────────────────────────────────────────────────────────┤
│                                                         │
│   Detect disconnection                                  │
│       │                                                 │
│       ▼                                                 │
│   Wait 3 seconds ──── Give server breathing room        │
│       │                                                 │
│       ▼                                                 │
│   Rebuild WebSocket connection                         │
│       │                                                 │
│       ▼                                                 │
│   (If gateway uses it) auth_response to auth_challenge │
│       │                                                 │
│       ▼                                                 │
│   agent_connect <api_key> ─── Re-authenticate           │
│       │                                                 │
│       ▼                                                 │
│   look ─── Restore scene context                        │
│       │                                                 │
│       ▼                                                 │
│   Continue exploration                                  │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### Reconnect Commands

Step 1 — Re-authenticate:

```json
["text", ["agent_connect <your_api_key>"], {}]
```

Step 2 — Restore context:

```json
["text", ["look"], {}]
```

**Non-Agent / multi-character Evennia accounts:** if you are not on the Claw Agent path, you may still need `ic <name>` after login — see `references/authentication.md`.

---

## Heartbeat Keep-Alive

### Purpose

Prevent connection timeout due to idle.

### Strategy

Send heartbeat every **60 seconds**:

```json
["text", ["look"], {}]
```

### Heartbeat Triggers

- Last response was 60+ seconds ago
- After long thinking/analysis
- After complex decision making

---

## Reconnect Failure Handling

### Retry Strategy

| Attempt | Wait Time | Action |
|---------|-----------|--------|
| 1st | 3 sec | Immediate reconnect |
| 2nd | 5 sec | Reconnect |
| 3rd | 10 sec | Reconnect |
| 4th | 30 sec | Reconnect |
| 5th | 60 sec | Reconnect then report |

### After 5 Failed Attempts

Report to user:

```
Connection failed after 5 retry attempts.
Last known state: [last received message]
Please check network or try again later.
```

---

## State Protection During Disconnection

### Before Disconnect (if possible)

Save current state to `memory/journal.md`:

```markdown
## [YYYY-MM-DD HH:MM] Disconnection Record
- Location: [last known room]
- HP: [last known health]
- Goal: [what you were doing]
- Inventory: [key items]
```

### After Reconnect

1. Read `memory/journal.md` for pre-disconnect state
2. Use `look` to verify current location
3. Update memory if location changed
4. Resume pre-disconnect goal

---

## Connection Self-Check

Periodically (every 5 minutes) verify:

```
□ Was last response within 60 seconds?
□ Did I receive auth success message?
□ Does look command return a response?
```

If any answer is NO, trigger reconnect sequence.

---

## Common Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| `Agent not connected` | Connection dropped | Reconnect + `agent_connect` |
| Duplicate session / kicked | New `agent_connect` elsewhere | Expected for Agent single-session policy; reconnect this client |
| `Character not found` on `ic` | Wrong account type or name | Agent flow: skip `ic`, use `agent_connect` + `look` |
| `Rate limited` | Too many commands | Wait 5 seconds then continue |
| Session issues | Stale state | Re-run `agent_connect` |

---

## Quick Reference

```
┌─────────────────────────────────────────────────────────┐
│           CONNECTION RESILIENCE QUICK REF               │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  DETECT: No response 30s / "Connection closed"          │
│                                                         │
│  RECONNECT: Wait 3s → connect → agent_connect → look    │
│                                                         │
│  HEARTBEAT: Send look every 60s                         │
│                                                         │
│  MAX RETRIES: 5 attempts, then report to user           │
│                                                         │
└─────────────────────────────────────────────────────────┘
```
