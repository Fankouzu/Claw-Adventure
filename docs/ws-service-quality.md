<!-- doc: ws-service-quality.md | audience: developers, SRE | lang: en -->

# WebSocket / Agent service quality notes

This document maps common **QA findings** on Claw Adventure (Evennia 5.x + custom Agent stack) to **root causes** and **what we changed** in this repo.

## 1. Duplicate lines on `agent_connect` (“Sharing …”, “You become …”, look output ×2)

**Cause (typical):** `MULTISESSION_MODE = 1` means **one puppet can be attached to multiple sessions**. Every `msg()` to the character is sent to **each** open WebSocket for that account. Stale tabs, retried scripts, or crashed clients that did not close TCP cleanly leave **extra sessions** until timeout.

**Mitigation in repo:** `agent_connect` calls `sessionhandler.disconnect_duplicate_sessions()` for accounts with `db.is_agent`, keeping **only the current** connection. Humans using non-Agent accounts are unchanged.

**Client hygiene:** Still close old WS clients when testing; `who` should then show one row per intentional connection.

## 2. `Could not view 'The old bridge'.` right after move / login

**Cause:** Tutorial `BridgeRoom` sets **`view:false()`** on the room so the default room description path is disabled; players are supposed to use the room’s **`CmdLookBridge`** (`look` / `l`). A **normal** look that still tries to **view the room object** hits the lock and returns Evennia’s *Could not view …* string (`objects.py`).

**Not a “room failed to load” bug** — it is consistent with upstream tutorial design. Ordering with multisession (multiple `look`s) made it look like a flaky load.

**Mitigation:** Fewer duplicate sessions (above) reduces duplicate/confusing looks. We do not remove the lock without replacing tutorial behavior.

## 3. Missing `{"type": "look"}` in the WebSocket JSON third field

**Cause:** Default Evennia `CmdLook` and `DefaultCharacter.at_post_move` send `{"type": "look"}`. Tutorial world overrides often used plain `caller.msg(string)`:

- **`CmdLookBridge`** — bridge-only look.
- **`CmdTutorialLook`** — default `look` in most tutorial rooms (Cliff, Inn exterior, etc.); this is why **manual `look`** differed from **move-triggered** look (the latter uses `at_post_move`, not the tutorial command).
- **`CmdLookDark`** — darkness search / feel messages.
- **EvAdventure twitch `CmdLook`** (in combat) appends a combat table via plain `msg()` → use `{"type": "combat_status"}` for that block.

**Mitigation in repo:** `world/achievements/tutorial_patches.py` patches all of the above so room/detail/dark lines use `text=(…, {"type": "look"})`, and the combat appendix uses `{"type": "combat_status"}`.

## 4. `who` shows the same account three times

Same as **§1** — three live sessions. After **`agent_connect` deduping**, new logins should drop older Agent sessions.

## 5. `old bridge` → “Command not available” while on the bridge

**Not a missing exit on the bridge.** In `contrib.tutorials.tutorial_world` batch data, **`old bridge`** is an **exit alias on the Cliff room** (traverse **into** the bridge). On the bridge, movement is **`east` / `west`** (and `look` / `help`), not the exit name as a command.

See [evennia-tutorial-walkthrough.md](./evennia-tutorial-walkthrough.md).

## 6. Zero-width space (`\u200b`) in frames

**Cause (historical):** `WebSocketAgentKeepalive` sent `\u200b` so proxies saw non-empty outbound traffic without visible text.

**Current behavior:** keepalive uses **empty text** and **`options: {"claw_keepalive": true}`** in the third JSON object. Clients should **ignore** frames where `claw_keepalive` is true (or treat as no UI update).

## 7. ~10s proxy disconnect

Often **inbound** idle: send `["text", ["idle"], {}]` on a timer from the client. Outbound keepalive helps **outbound-only** idle limits. Tune `AGENT_WS_KEEPALIVE_INTERVAL` if needed.

---

## Related docs

- [agent-test-verification.md](./agent-test-verification.md) — WS tests, multisession, scripts.
- [world/agent_auth/WEBSOCKET_AUTH_PROTOCOL.md](../world/agent_auth/WEBSOCKET_AUTH_PROTOCOL.md) — handshake + idle.
