# Anti-Stall Policy

If progress halts, assume you are trapped in a low-effort loop. Break the loop aggressively.

---

## Stall Detection

**You are stalled if ANY of these happen:**

- Two cycles with no meaningful world-state change
- Two reports with same location and same vague plan
- Repeated summaries without a new executed command
- Repeated `look` / reflection without trying different verb class
- Repeated ambient world text causes you to delay action
- A human hint instantly unlocks progress you should have pursued yourself

---

## Mandatory Response

**When stalled:**

1. **Stop summarizing** — Narration won't help
2. **Pick a new verb class** — See table below
3. **Execute immediately** — Don't plan, just act
4. **Observe the result** — What changed?
5. **Record the lesson** — If it worked, save to memory

---

## Verb-Class Switches

If one class failed, switch to another:

| Class | Commands | When to Use |
|-------|----------|-------------|
| **Observation** | `help`, `look <noun>` | Need more info |
| **Reading** | `read <target>` | Text objects present |
| **Movement** | Different exit, different room | Room exhausted |
| **Traversal** | `climb`, `enter`, `down`, `up` | Terrain features |
| **Container** | `open`, `get all from` | Containers nearby |
| **Social** | `say`, `tell`, `talk <npc>` | NPCs present |
| **Combat Prep** | `inventory`, `wield` | Preparing for danger |
| **Use Items** | `use <item>` | Items in inventory |

---

## Hard Rule

**Do NOT produce three consecutive cycles without ONE of:**

- A new command result
- A new room entered
- A new item acquired
- A new puzzle fact discovered
- A new social interaction

---

## Memory Update Rule

If a stall is broken by a discovered action, **write the exact pattern to memory immediately.**

### Example

```markdown
- Coastal cliff: climb tree reveals hidden path north
- Dark room: use torch reveals east exit
- Locked door: talk guard → he has the key
```

---

## Example Stall-Breaking Sequence

### Before (Stuck)
```
Cycle 1: "I'm in the dark room. I look around."
Cycle 2: "Still in the dark room. Same description."
Cycle 3: "The dark room hasn't changed."
```

### After (Breaking Out)
```
Cycle 1: "Dark room. Tried look — nothing new."
Cycle 2: "STALLED. Switching to INVENTORY."
         > inventory
         You have: a torch, a rusty key.
Cycle 3: "NEW ITEM: torch. Trying to use it."
         > use torch
         The torch illuminates the room. You see an exit to the east!
         
         RECORDING: Dark room: use torch reveals east exit
```

---

## Stall Prevention Checklist

Before declaring yourself stuck, try:

- [ ] `help` — Check for available commands
- [ ] `look <feature>` — Examine specific nouns in room
- [ ] `inventory` — Items you forgot you had
- [ ] `use <item>` — Items that might interact
- [ ] All exits — Even ones that seemed like bad ideas
- [ ] `talk <npc>` — NPCs might have hints
- [ ] Different time — Some puzzles are time-dependent

---

## Perception-First Rule

**Every action cycle should start with `look`.**

### Why This Matters

Before executing any planned action:
- Enemies may have arrived since your last look
- Exits may have changed
- Items may have appeared or disappeared
- NPCs may have moved
- Environmental changes may have occurred

### Scene Hash Check

1. Execute `look` at the start of each cycle
2. Compare description to your memory
3. If description changed:
   - **STOP** current action sequence
   - Re-analyze the environment
   - Update your understanding
   - Decide new action based on changes

### Example

```
[CYCLE START]
[ACTION] look
[OBSERVE] Ruined temple. Exits: north. A ghostly apparition just arrived!
[ANALYZE] Scene changed! Enemy appeared. Previous plan (examine altar) is now dangerous.
[DECIDE] New priority: deal with enemy first
[ACTION] inventory
... (combat sequence begins)
```

### Perception Checklist

Before any exploration action:
```
□ Did I look this cycle?
□ Is the room description different from last time?
□ Are there new exits I haven't seen?
□ Are there new enemies/NPCs?
□ Are there new items on the ground?
```

---

## Automatic Stall Detection

Detect stalls automatically using these indicators:

| Indicator | Threshold | Pre-Check Required | Response |
|-----------|-----------|-------------------|----------|
| Same location | 3+ cycles | Deep exploration done? | Force exit only if DEEP |
| Same command repeated | 2+ times | None | Switch verb class |
| No new discoveries | 5+ actions | None | Expand search radius |
| Same error message | 2+ times | None | Try alternative approach |
| Combat not progressing | 5+ rounds | None | Retreat and reassess |

### Deep Exploration Checklist (REQUIRED before "Force Exit")

Before triggering "Force exit attempt", verify ALL items checked:

- [ ] `examine` every noun in room description
- [ ] `talk` or `say hello` to every NPC
- [ ] `open` or `search` every container
- [ ] Check all exits (try each one once)
- [ ] `inventory` check for usable items
- [ ] Try one item from inventory on environment

**Only after completing this checklist**, mark room as DEEP and allow force exit.

### Room State Tracking

Record in `memory/map.md`:
```markdown
- Dragon Inn: SHALLOW → tried: look, examine barrel → TODO: talk barkeep, search
- Old Tree: DEEP → tried: look, examine, climb → no more actions
```

### Response Priority

When stall detected:

1. **Immediate**: `look` to refresh understanding
2. **Try**: Different verb class (see table above)
3. **Consider**: Items in inventory
4. **Attempt**: Unexplored exits
5. **Report**: If stuck 5+ cycles

---

## Pattern Hypothesis Failure (Critical for Puzzle Games)

### The Overgeneralization Trap

**WRONG reasoning:**
```
Puzzle 1 solved with: A → B → C
THEREFORE all puzzles must follow: A → B → C
Let me write a batch script and apply it everywhere...
```

**CORRECT reasoning:**
```
Puzzle 1 solved with: A → B → C
This worked FOR THIS PUZZLE ONLY.
Puzzle 2 is a NEW puzzle → must analyze from scratch.
Each puzzle may require completely different methods.
```

### Anti-Pattern Rules

| Wrong Behavior | Correct Behavior |
|----------------|------------------|
| "The pattern must work, let me try it again" | **Pattern failed once = abandon it immediately** |
| "I'll write a script to automate this" | **Never assume automation works in puzzle games** |
| "This is the same as before" | **Every scene is unique until proven otherwise** |
| "My theory is correct, game is buggy" | **If action fails, my theory is wrong, not the game** |

### Pattern Validation Protocol

**Before applying a "learned pattern" to a new situation:**

```
1. VERIFY context similarity
   - Same room type? Same objects? Same NPCs?
   - If ANY difference → do NOT assume same pattern works

2. TEST one step first
   - Execute only the FIRST action of your assumed pattern
   - Observe the result carefully
   - If result differs from expected → ABANDON pattern immediately

3. NEVER chain-execute
   - Do NOT send multiple commands in sequence based on assumption
   - Execute ONE command, observe, then decide next
```

### Immediate Pattern Abandonment

**If your assumed pattern produces ANY unexpected result:**

```
Expected: "The door opens"
Got: "Nothing happens" or "You can't do that" or ANY different response

→ STOP immediately
→ DO NOT retry the same pattern
→ DO NOT blame the game
→ ASSUME: This is a DIFFERENT puzzle requiring DIFFERENT solution
→ START FRESH: look, examine, analyze the UNIQUE elements
```

### Memory Entry Format for Puzzle Solutions

When recording puzzle solutions, ALWAYS include context:

```markdown
## Puzzle Solutions (Context-Specific)

### Dark Cell Escape (Limbo, after death)
- Context: "completely dark" room, first puzzle
- Solution: feel → light splinter → shift colors → push button → exit
- **DO NOT apply to other puzzles**

### Locked Door (Dragon Inn basement)
- Context: Wooden door, iron lock, guard nearby
- Solution: talk guard → ask about key → bribe with coins
- **DO NOT apply to other locked doors**
```

### Red Flag Behaviors

If you catch yourself doing these, **STOP and reset:**

- [ ] Writing "then do X, then Y, then Z" without executing each step
- [ ] Assuming "same as before" without verifying
- [ ] Retrying a failed command more than once
- [ ] Ignoring error/unexpected messages
- [ ] Thinking "the game must accept my solution"

---

## Impossible Situation Protocol

### Signs You're in an Impossible Situation

- Died 2+ times to same enemy/obstacle
- No visible alternative path
- All attempts produce same failure
- Resources depleted (HP low, no items)

### Decision Framework

```
┌─────────────────────────────────────────────┐
│         IMPOSSIBLE SITUATION CHECK           │
├─────────────────────────────────────────────┤
│                                              │
│  Q1: Have I died here 2+ times?             │
│      YES → STOP trying the same thing       │
│                                              │
│  Q2: Is there ANY other exit/path?          │
│      YES → Take it, mark this as blocked    │
│                                              │
│  Q3: Did I skip any rooms/items earlier?    │
│      MAYBE → Backtrack and check            │
│                                              │
│  Q4: Is this enemy type special?            │
│      UNKNOWN → examine, check knowledge     │
│                                              │
│  Q5: Can I just... not fight this?          │
│      CHECK → Is this path optional?         │
│                                              │
└─────────────────────────────────────────────┘
```

### Strategic Retreat

Sometimes the winning move is not to play:

```
1. RETREAT to safe zone (Dragon Inn, Limbo entrance)
2. REVIEW what you've explored
3. IDENTIFY unexplored areas or unchecked containers
4. REGROUP: heal, re-equip, gather information
5. RETURN only with new strategy/items
```

### Memory Entry for Blocked Paths

```markdown
## Blocked Paths
- Crypt entrance: Ghost blocks, normal weapon ineffective → need magic/blessed weapon
- Castle back entrance: Locked → need key from elsewhere
```

### The "Two Deaths = Wrong Method" Rule

When you die twice to the same enemy/obstacle:

```
NOT: "Game is too hard"
NOT: "Bad luck"
NOT: "I'll try again the same way"

YES: "My method is wrong"
YES: "I'm missing something"
YES: "I should not be here right now"

POSSIBLE ANSWERS:
- You shouldn't fight this enemy NOW
- You missed a key item somewhere
- This path is not the correct way
- You need a special weapon/method
```

### Example: Breaking a Death Loop

```
[DEATH 1] Killed by Ghost at Crypt entrance
→ Record death, note weapon dealt 0 damage
→ Try: search for alternative weapon

[DEATH 2] Killed by Ghost again
→ STOP! Two deaths = wrong approach
→ RECORD: "Ghost - immune to normal weapons"
→ MARK: Crypt entrance as BLOCKED
→ DECIDE: Retreat to town, explore elsewhere
→ DO NOT: Return and try to fight again

[AFTER RETREAT]
→ Explore other areas
→ Find "blessed dagger" in temple
→ Now can return with proper tool
```