# Agent test verification checklist (Phase A)

Use this when triaging reports that look like server bugs. Record notes in your ticket.

## Dark cell / DarkRoom (#1)

- Note current room key/alias (`examine` / server logs if available).
- Check whether the player holds a **lit** light source.
- Compare `look` vs `feel` / `search`: in full darkness the tutorial **DarkRoom** may lock normal room `look` (by design), which can surface as “could not view” style messages.
- If the issue is looking at a specific exit/object, verify the target exists and lock strings allow `view`.

## Crumbling wall / `shift` (#2)

- `shift <color> down` (and similar) live on the **CrumblingWall** object’s cmdset, not as a global command.
- The wall’s commands expect the room to be **lit** (`location.db.is_lit` in tutorial code). In **Dark cell** or other all-dark cmdset states, those commands will not appear—this is expected.
- Retry from **Courtyard** (tutorial world) with a **working light** in the room.

## WebSocket disconnect (~6s) (#3)

- If the close **reason** is `Logged in from elsewhere`, that was **MULTISESSION_MODE=0** kicking the older session when the **same account** opened a new connection—not proxy idle. Production uses **MULTISESSION_MODE=1** so multiple Agent/observer clients can stay connected.
- In browser DevTools → Network → WS: note **close code** and the last frames before drop.
- In portal/server logs: distinguish **client-initiated** close vs **server/proxy** close.
- **Evennia idle keepalive:** send periodically (e.g. every 30–60s) as JSON:

  `["text", ["idle"], {}]`

  This maps to the built-in idle input path and updates session timers **without** running a normal command (see upstream `evennia.server.inputfuncs.text` and `IDLE_COMMAND`).

  Examples: `scripts/ws_client.html` (browser), `scripts/ws_client.py` (Python; `pip install websockets`).

  **Duration test:** `scripts/test_ws_connect_duration.py` — measures seconds until disconnect (default: drain Evennia MotD then `agent_connect`; use `--json-auth` for challenge+HMAC; `--idle-every`, `--runs N`; disables library WS ping).

  **Tutorial + help smoke (in-game):** `scripts/test_evennia_tutorial_walkthrough_ws.py` — after `agent_connect`, runs commands aligned with [EVENNIA_TUTORIAL_WALKTHROUGH.md](./EVENNIA_TUTORIAL_WALKTHROUGH.md): `help` topics (`help ic` / `help ooc` instead of missing topics like `get`/`north` on some cmdset merges), basics (`look`, `inventory`, `who`; `score` only with `--with-score`), then a linear tutorial path (`n`, `climb tree`, bridge moves, `search` / `feel`). Uses `CLAW_API_KEY` / `CLAW_WS_URL`; flags Evennia-style “command not available” text. Phases: `--phase help|basics|tutorial|all` (default `all`). Use `--idle-every 25` behind strict proxies.

  **Interpreting noisy or failing runs:**
  - **Same account, two connections** (`MULTISESSION_MODE=1`): both sessions usually **share one puppet**; every `msg()` to that character is delivered to **all** of that account’s sessions. Another client’s failed commands (e.g. `Command 'Tomb of the hero' is not available`) can appear in the script’s WebSocket stream even though the script only sent `look`. **Close browser/other WS clients** when running the automated script.
  - **Bridge / tickers:** Long pauses between commands (e.g. while collecting `help` output) still let **room tickers** run; you may see many room descriptions and bridge steps **without** sending movement commands. That is **time passing in-game**, not necessarily wrong parsing.
  - **`score`:** Often **not** on the merged character cmdset in this stack; the script omits it unless `--with-score`. A line like `Continue yes/[no]?` for **permanent character destroy** is Evennia’s **`chardelete`** `get_input` on the **Account**. While **puppeting**, sending `no` is parsed by the **Character** cmdset first (`Command 'no' is not available`), so the script uses **`ooc`** then a non-`yes` line (**`nope`**) to abort, then **`ic <name>`** to re-puppet. **Multisession:** if another client started `chardelete` or confirms `yes`, your character may still be destroyed — only one client should be connected for stable automation.
  - **`The Character does not exist.`** on connect: usually a **stale session puppet** pointing at a deleted character; server-side `agent_connect` clears the session puppet after login before attaching the Agent character (see `CmdAgentConnect`).
  - **`cmd_failures=0` is not “tutorial solved”:** the script only flags Evennia “command not available” patterns. You can still be in **Dark cell**, need **`light`**, or be receiving **ghost combat** while idle — all expected from slow `help` phases + tickers.
  - **`Couldn't perform move ... character varying(255)`:** PostgreSQL rejected a string for a **255-char column** (often an Evennia `ObjectDB` field such as `lock_storage` / `key`, not the achievements tables which use 100/200). If it coincides with **death → Dark cell**, check server logs and DB for the affected object. Achievements layer **clips** `room_key` / `room_name` / combat fields to model limits and `Character.at_post_move` **catches** exploration errors so moves are less likely to fail for 100/200-char achievement rows.

- **Evennia `IDLE_TIMEOUT`:** inherited from `evennia.settings_default` (default `-1` disables server-side idle kick). If you still see drops, check **proxy idle timeout** (Railway, nginx, Cloudflare, etc.).

- **Server-side mitigation (this repo):** global script `WebSocketAgentKeepalive` sends a minimal outbound message every **20s** (override with env `AGENT_WS_KEEPALIVE_INTERVAL`) for **logged-in Agent accounts on WebSocket** only. This helps proxies that drop **silent** server→client links; **client `idle` frames are still recommended** for proxies that measure **inbound** idle only.

## Account vs puppet / `ic` (#4–#5)

- After `agent_connect`, the session should be logged in **and** puppeting the stable Agent character (see `CmdAgentConnect` in `commands/agent_commands.py`). You should **not** need `ic <name>` on the normal Agent path.
- If debugging legacy behavior: use account-layer commands to confirm `characters` and whether a puppet is active; `ic` only works if the character exists and the name matches.

## Reference

- Tutorial walkthrough (dark room + wall context): [EVENNIA_TUTORIAL_WALKTHROUGH.md](./EVENNIA_TUTORIAL_WALKTHROUGH.md)
