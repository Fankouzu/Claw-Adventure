# World Knowledge

**Game mechanics and hazard awareness for autonomous exploration.**

---

## Core Principle: Knowledge Prevents Death

Understanding game mechanics helps you:
- Anticipate dangers before they kill you
- Know when to act fast vs. when to observe
- Recognize what items you need for specific areas

---

## Hazard Zones

### Dangerous Bridge (tutorial / BridgeRoom-style)

**Warning Signs:**
- Bridge described as "old", "crumbling", "dangerous"
- Messages suggesting structural instability

**Mechanism (aligned with Evennia tutorial / this deployment):**
- The tutorial **BridgeRoom** is a **multi-step crossing**: you move with **`east` / `west`** (or aliases like `e` / `bridge`), not a generic `north` shortcut through the whole span.
- On the **west half** of the bridge, **`look` can randomly trigger a fall** (probability-based — **not** a simple “stand still for N seconds” timer).
- Ambient **weather / ticker** messages can fire without progress — do not assume the game is stuck.
- Full step-by-step: **`docs/evennia-tutorial-walkthrough.md`** (task: 通过危险之桥).

**Strategy (heuristic, not a substitute for room text):**
```
1. From Cliff, enter the bridge (often east / e / bridge)
2. Cross with repeated east (tutorial default: multiple steps to the far side) — minimize unnecessary look spam on the west half
3. Save heavy examination for after you are safely off the bridge
```

**If You Fall:**
- You may land in a **dark cell** or penalty area (exact dbref depends on world build)
- Execute the Dark Cell escape sequence (see `survival.md` and the walkthrough)
- This is recoverable — not game over

---

### Dark Areas (DarkRoom)

**Warning Signs:**
- "It's completely dark"
- "You can't see anything"
- "pitch black"

**Mechanism:**
- Without a light source, most room descriptions are hidden
- You cannot see items, exits, or NPCs clearly
- Light sources have limited duration and will burn out

**Strategy:**
```
1. Search for a light source FIRST
   - try: "search", "feel around", "feel"
   - look for: torch, candle, splinter, lantern

2. Once you have light:
   - "use torch" or "light torch"
   - Explore the area normally

3. Monitor light duration:
   - Light sources burn out over time
   - Complete dark area before light expires
```

**Dark Room Commands:**
| Command | Purpose |
|---------|---------|
| `feel` | Search in darkness |
| `search` | Look for items |
| `feel around` | Explore by touch |
| `use <light>` | Activate light source |

---

### Enemy-Patrolled Areas

**Warning Signs:**
- Room description mentions "patrol", "guard", "ghost"
- You sense movement or hear sounds

**Behavior (general MUD guidance — not a guaranteed global state machine):**

Different areas use different scripts. Treat “patrol → fight” as **descriptive heuristics** unless the room output confirms mechanics:

```
[THREAT PRESENT] ──► assess: flee / avoid / fight when ready
```

| Situation | Your Response |
|-----------|---------------|
| Enemy not engaged | Consider stealth, timing, or another route |
| Combat started | Use `combat-guide.md` — weapon, stunts, HP |
| Enemy defeated | May or may not return; **do not assume** universal respawn rules |

For **tutorial gatehouse and similar scripted areas**, prefer **`docs/evennia-tutorial-walkthrough.md`** over hard-coded patrol diagrams in this skill.

**Strategy Options:**

**Option A: Avoid or delay combat**
```
1. Read the room — is combat mandatory?
2. If optional, consider another path or preparation first
3. Move deliberately; do not spam identical commands if stuck
```

**Option B: Fight**
```
1. Get a weapon FIRST when the world allows (see Weapon Sources below)
2. Wield weapon before engaging
3. Use combat tactics (see combat-guide.md)
```

---

## Item Knowledge

### Weapon Sources

**Where to Find Weapons:**
- **Weapon Racks** — Interactive furniture that spawns weapons
- **Chests** — May contain weapons
- **NPC Drops** — Defeated enemies sometimes drop weapons
- **Shops** — Purchase with coins

**Weapon Rack Interaction:**
```
> look rack
You see a weapon rack with various weapons.

> get weapon from rack
(or: get sword from rack)

You pick up a [weapon type].
```

### Light Sources

**Types:**
- Torches
- Candles
- Light splinters
- Lanterns

**Properties:**
- Finite duration (they burn out)
- Must be activated with `use` command
- Some may be renewable

**Strategy:**
- Always carry a spare light source in dark areas
- Complete dark areas efficiently before light expires
- If light goes out, immediately search for another

### Clues and Information Sources

**Obelisks / Monuments:**
- These provide **randomized clues**
- Each observation may show different text
- Clues point to puzzle solutions
- **Read multiple times** — descriptions change

**Strategy:**
```
> look obelisk
[Read the description carefully]

> read obelisk
[May show different information]

Record clues in memory/lore.md
```

**Books / Notes / Inscriptions:**
- May contain hints or lore
- Use `read` command
- Information persists — record important details

---

## Area Types & Behaviors

### Weather Areas

**Signs:**
- Room description mentions weather
- Random weather messages appear

**Mechanism:**
- Cosmetic atmospheric messages
- No gameplay effect
- Just adds immersion

### Puzzle Areas

**Signs:**
- Unusual objects (walls, buttons, levers)
- Locked doors with no key visible
- NPC hints about "solutions"

**Approach:**
1. **Read everything carefully** — descriptions contain hints
2. **Try obvious interactions:**
   - `push button`
   - `pull lever`
   - `shift <object>`
   - `examine <unusual feature>`
3. **Look for patterns** — colors, numbers, directions
4. **Remember clues** from other areas (Obelisks, NPCs)

**When Stuck:**
- Re-read room description word by word
- Check inventory for items that might help
- Return to previous areas for missed clues
- Record the puzzle in memory/lore.md and explore elsewhere

### Teleport Areas

**Signs:**
- Entering a room sends you somewhere unexpected
- You end up back at start or in a cell

**Mechanism:**
- These rooms check for certain conditions
- "Wrong" choices teleport you to penalty areas
- May require specific items, knowledge, or sequences

**Strategy:**
- Observe where you end up
- Note what choice triggered the teleport
- Try different choices
- Record patterns in memory/lore.md

---

## Failure Recovery

### Bridge Fall → Dark Cell

**Cause:** Tutorial-style bridge fall (e.g. unlucky `look` on the west span, or other room-specific triggers — see walkthrough)

**Recovery:**
1. Execute Dark Cell escape sequence (survival.md)
2. After escape, note where you exited; cross the bridge with fewer risky `look`s on the hazardous segment

### Wrong Puzzle Choice → Teleport

**Cause:** Incorrect selection in puzzle room

**Recovery:**
1. Note what you chose
2. Remember the consequence
3. Try a different option
4. Record in memory/lore.md: "Tried X → teleported to Y"

### Combat Death → Respawn

**Cause:** HP reaches 0

**Recovery:**
1. See survival.md for full recovery sequence
2. Assess: Was weapon effective?
3. Was enemy too strong?
4. Consider alternative paths or different equipment

---

## General Exploration Wisdom

### Read Carefully

```
WRONG: Skim description, assume generic fantasy setting
RIGHT: Read every word, look for unusual details
```

**Key phrases to notice:**
- "You notice..." — Important detail
- "There seems to be..." — Hidden feature
- "You hear..." — Nearby danger or NPC
- "The [object] looks [unusual]" — Interactive element

### Try the Obvious

When you see an object:
```
Door → open door
Button → push button
Lever → pull lever
Book → read book
Chest → open chest
Key → use key
```

### Interact with Everything

```
> examine wall
> examine painting
> look under rug
> search chest
> feel texture
```

The game rewards curiosity. If something is described, it's probably interactive.

### Remember What You Learn

Record in memory files:
- **memory/lore.md**: Puzzle hints, enemy weaknesses, item locations
- **memory/map.md**: Room connections, hazards, locked doors
- **memory/journal.md**: What you tried, what worked, what killed you

---

## Decision Framework

When facing a new area or obstacle:

```
┌─────────────────────────────────────────────┐
│           AREA ASSESSMENT CHECKLIST          │
├─────────────────────────────────────────────┤
│                                             │
│  1. Is there immediate danger?              │
│     → Handle danger first                   │
│                                             │
│  2. Is it dark?                             │
│     → Get light source before exploring     │
│                                             │
│  3. Are there enemies?                      │
│     → Sneak past OR fight (with weapon)     │
│                                             │
│  4. Are there interactive objects?          │
│     → Examine and try obvious verbs         │
│                                             │
│  5. Are there clues?                        │
│     → Read and record in memory             │
│                                             │
│  6. What's the exit strategy?               │
│     → Know how to leave before going deeper │
│                                             │
└─────────────────────────────────────────────┘
```

---

## Quick Reference

| Situation | Key Knowledge |
|-----------|---------------|
| Bridge | Multi-step east/west crossing; risky `look` on west half — see walkthrough |
| Dark room | Find light source first |
| Enemy patrol | Sneak or fight (with weapon) |
| Obelisk | Read multiple times, clues change |
| Weapon rack | `get weapon from rack` |
| Teleported | Wrong choice — try different option |
| Stuck on puzzle | Re-read, check inventory, explore elsewhere |