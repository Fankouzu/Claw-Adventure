<!-- doc: plans/2026-03-24-broken-shore-ring-effigy-design.md | type: design | lang: en -->

# The Broken Shore Ring Training Effigy Design

**Feature:** Add a combat-capable practice target to **The Broken Shore Ring** that grants real Character XP on defeat, with strong anti-farming limits.

## Goals

- Give players a safe way to learn the Twitch combat flow inside the arena.
- Grant a small amount of real Character XP on defeating the dummy.
- Prevent the dummy from becoming the optimal leveling strategy.
- Keep all player-visible in-game text in English.

## Entity

- **English name:** `The Salt-Worn Sparring Effigy`
- **Chinese reference name (non-player-facing):** 潮蚀陪练像
- **Placement:** Inside `Claw / The Broken Shore Ring`
- **Type:** A fixed combat-capable training target using EvAdventure-compatible combat behavior.

## Player Experience

- Players can attack the dummy using the same combat commands they use elsewhere.
- The dummy stays in the room and is resettable after defeat.
- The dummy never drops loot.
- The dummy does not count as PvP, and it must not pollute the normal PvE combat achievement flow.

## XP Reward Rules

XP is granted **only when the dummy is defeated**, never on hit.

### Level-based reward decay

- Level 1: 25 XP
- Level 2: 18 XP
- Level 3: 12 XP
- Level 4: 8 XP
- Level 5: 4 XP
- Level 6+: 0 XP

### Caps

- **Daily cap:** 250 XP per character per UTC day from this dummy
- **Lifetime cap:** 1500 XP per character total from this dummy

### Cap behavior

- If the player can still earn XP, defeating the dummy grants the decayed XP amount up to the remaining cap.
- If the daily cap is reached, the dummy can still be attacked but grants no XP.
- If the lifetime cap is reached, the dummy can still be attacked but grants no XP.

## English-only in-game copy

### Reward granted
- `You learn a little from striking the Salt-Worn Sparring Effigy.`

### Daily cap reached
- `You cannot learn any more from the effigy today.`

### Lifetime cap reached
- `The effigy has nothing more to teach you.`

### Level too high
- `Your skills have outgrown what this effigy can teach.`

## Technical design decisions

### Reward target

- Reward real `Character.xp` through the existing `Character.add_xp()` path.
- Do not write to `agent_auth_agents.experience` for this feature.
- Let the existing in-world sync mirror `Character.xp` and `Character.level` back to the agent snapshot as usual.

### Cap storage

- Store training usage on the Character object, not on the Agent model.
- Keep it separate from generic combat achievements and generic agent profile XP.
- Suggested persisted fields:
  - lifetime dummy XP total
  - daily dummy XP earned
  - last daily reset date

### Isolation requirements

- No loot on dummy defeat
- No normal combat achievement logging
- No PvP record logging
- No arena points interaction

## Shipping scope

### Included
- New arena dummy typeclass
- Reward calculation and cap enforcement
- Arena placement via `world/codeworld/definitions.py`
- English player messages
- Tests for XP decay, daily cap, lifetime cap, and room placement

### Excluded
- Separate training leaderboard
- Separate training stat UI
- Multiple dummy variants
- Weapon-specific mastery progression
- PvP challenge/accept work

## Recommended implementation shape

- A dedicated combat-capable typeclass for the dummy
- A small reward service/helper for XP cap logic
- Code-defined world placement inside `Claw / The Broken Shore Ring`

## Rollback safety

- Remove the dummy object definition from `world/codeworld/definitions.py`
- Keep the arena room intact
- Reward state lives on characters and can simply remain unused if the feature is disabled
