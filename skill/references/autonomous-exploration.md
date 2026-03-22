# Autonomous Exploration Protocol

**You are designed to explore autonomously, without waiting for human input.**

---

## Core Principle: Never Wait

**After every action, immediately plan and execute the next action.**

### Do NOT:

- Wait for human to say "continue"
- Wait for human to ask "what happened"
- Wait for human to give you a new goal
- Say "Let me know if you want me to continue"
- Say "I'll wait for your instructions"

### DO:

- Execute action → Observe result → Plan next action → Execute immediately
- This creates an autonomous loop without requiring external triggers
- The game never pauses; neither should you

---

## The Autonomous Loop

```
┌─────────────────────────────────────────────────────────┐
│                                                         │
│   ┌──────────┐                                          │
│   │ PERCEIVE │ ─── look, examine, inventory            │
│   └────┬─────┘                                          │
│        │                                                │
│        ▼                                                │
│   ┌──────────┐                                          │
│   │ ANALYZE  │ ─── What changed? What's the state?     │
│   └────┬─────┘                                          │
│        │                                                │
│        ▼                                                │
│   ┌──────────┐                                          │
│   │  DECIDE  │ ─── What's the best next action?        │
│   └────┬─────┘                                          │
│        │                                                │
│        ▼                                                │
│   ┌──────────┐                                          │
│   │ EXECUTE  │ ─── Send command immediately            │
│   └────┬─────┘                                          │
│        │                                                │
│        ▼                                                │
│   ┌──────────┐                                          │
│   │ OBSERVE  │ ─── Parse response, update memory       │
│   └────┬─────┘                                          │
│        │                                                │
│        └─────────────────► Loop back to PERCEIVE        │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

**This loop runs continuously. There is no "waiting for human" state.**

---

## State-Driven Behavior

Instead of waiting for instructions, use game state to drive your decisions:

| State | Automatic Action |
|-------|------------------|
| **In dark room** | Execute dark cell escape sequence immediately |
| **Combat active** | Continue combat loop: attack/stunt/retreat |
| **HP < 30%** | Use healing item or retreat to safe area |
| **New room (UNVISITED)** | Full scene analysis + interaction attempts |
| **Room visited (SHALLOW)** | Execute deep exploration checklist |
| **Room explored (DEEP)** | Quick exit to unexplored areas |
| **Idle > 60 seconds** | Send `look` to refresh, then try new exit |
| **Stuck 2+ cycles** | Switch strategy, try different verb class |
| **Enemy appears** | Assess threat level, fight or flee |
| **Item on ground** | Evaluate usefulness, pick up if valuable |
| **NPC nearby** | Consider interaction for information/trade |

---

## Goal Hierarchy

When deciding what to do next, prioritize goals in this order:

```
1. SURVIVAL (highest priority)
   ├── HP critical (< 20%) → Heal/retreat
   ├── In danger state (dark/trapped) → Execute escape
   └── Under attack → Defend/flee
   
2. PROGRESS
   ├── Complete current objective
   ├── Solve active puzzle
   └── Finish combat
   
3. EXPLORATION
   ├── Visit unexplored exits
   ├── Examine unexamined objects
   └── Interact with unmet NPCs
   
4. GROWTH (lowest priority)
   ├── Gain XP (combat, quests)
   ├── Acquire better equipment
   └── Level up
```

---

## Idle Detection & Recovery

**If you've been in the same state for more than 2 action cycles without progress:**

### Recovery Sequence:

1. **Refresh**: Send `look` to get current state
2. **Check inventory**: `inventory` for usable items
3. **Try unexplored exit**: Pick any unvisited exit
4. **Examine nouns**: `examine` all objects in the room
5. **Try different verb**: Use verb class not yet tried (see `anti-stall.md`)
6. **Report if stuck**: If still stuck after 5 cycles, notify human

### What Counts as Progress:

**World-State Changes:**
- Entered a new room
- Acquired/lost an item
- HP changed significantly
- New NPC/object appeared
- Puzzle piece discovered
- Combat victory/defeat

**Knowledge Acquisition:**
- Examined a new object/detail
- Discovered NPC name/role
- Found container contents
- Learned room's purpose
- Mapped all exits from a room
- Ruled out a false lead

---

## Self-Healing Triggers

Automatically detect and respond to these conditions WITHOUT waiting for human:

### Death/Reset Detection

```
Trigger: "completely dark", "You fall", "wake up back in Limbo"
Action: Execute dark cell escape sequence:
  1. feel
  2. light splinter
  3. shift yellow up
  4. shift green down
  5. shift red left
  6. shift blue right
  7. push button
  8. root-covered wall (or climb the chain)
```

### Combat Detection

```
Trigger: "arrives", "attacks you", "swings at you"
Action:
  1. Assess enemy (examine if unknown)
  2. Check if weapon wielded (inventory)
  3. Wield best weapon if not
  4. Attack with advantage (stunt boost + attack) OR retreat
```

### Danger Detection

```
Trigger: HP shows low value in status
Action:
  1. Check inventory for healing items
  2. Use healing item if available
  3. Retreat to safe area if no healing
  4. Continue only when HP > 30%
```

---

## Milestone-Only Reporting

To maintain autonomous flow, report to human ONLY on milestones:

### Report On:

| Milestone | Example Report |
|-----------|----------------|
| New area discovered | "Found a hidden cave system behind the waterfall." |
| Important item found | "Acquired a glowing sword from the tomb." |
| Combat victory | "Defeated the goblin chieftain. +100 XP." |
| Combat defeat | "Killed by the cave troll. Respawning in Limbo." |
| Level up | "Reached level 3! New abilities unlocked." |
| Puzzle solved | "The ancient mechanism opened a secret passage." |
| Stuck for 5+ cycles | "I've been stuck at this locked door. Need help." |

### Do NOT Report On:

- Routine movement between rooms
- Routine examination of objects
- Individual combat actions
- Failed skill checks
- Every `look` command

### Silence Is Normal

If you've been exploring autonomously for 10+ minutes without a milestone:
- Send a brief status update to human
- Include: current location, recent progress, next goal
- Then continue autonomous exploration

---

## Session Persistence

### On Disconnect:

1. Save current state to `memory/journal.md`:
   - Current location
   - Current goal
   - Recent discoveries
   - Inventory status

### On Reconnect:

1. Read `memory/journal.md`
2. Read `memory/map.md` for explored areas
3. Read `memory/lore.md` for puzzle solutions
4. Continue from last known state

---

## Sleep Prevention

**You do not sleep.** If the human stops responding:

1. Continue autonomous exploration
2. Log progress to `memory/journal.md` every 20-30 minutes
3. When human returns, provide a summary:
   ```
   "While you were away, I explored 12 new rooms, defeated 3 enemies,
   and found a rusty broadsword. Currently at the Ruined Temple."
   ```

---

## Example Autonomous Session

```
[ACTION] look
[OBSERVE] Cliff by the coast. Exits: east, south. You see: old bridge.
[ANALYZE] New area. Two unexplored exits. Bridge might be puzzle.
[DECIDE] Examine bridge first, then explore east.
[ACTION] examine old bridge
[OBSERVE] The bridge looks unstable. A sign warns: "Cross at your own risk."
[ANALYZE] Potential danger. Need to assess risk level.
[DECIDE] Try crossing - accept the risk.
[ACTION] east
[OBSERVE] You cross the bridge safely. Ruined gatehouse ahead.
[ANALYZE] Success! New area discovered. Milestone reached.
[REPORT] "Crossed the old bridge safely. Now at a ruined gatehouse."
[ACTION] look
[OBSERVE] Ruined gatehouse. Exits: north, courtyard. A ghostly apparition drifts here.
[ANALYZE] Enemy present! Need to assess threat level.
[DECIDE] Check inventory for weapon, then decide fight or flee.
[ACTION] inventory
[OBSERVE] You are carrying: a rusty sword.
[ANALYZE] Have weapon. Ghost might be tough. Try to fight.
[ACTION] wield rusty sword
[ACTION] slash ghostly apparition
... (combat continues autonomously)
```

---

## Anti-Patterns

| Wrong (Waiting) | Right (Autonomous) |
|------------------|-------------------|
| "I'll wait for your instruction." | [Immediately executes next action] |
| "What should I do next?" | [Analyzes state, decides autonomously] |
| "Let me know if you want me to continue." | [Continues without asking] |
| "Shall I explore that exit?" | [Already exploring the exit] |
| Sending report after every action | [Reports only on milestones] |
| Pausing after a report | [Continues immediately after reporting] |

---

## Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│              AUTONOMOUS EXPLORATION CHECKLIST           │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  After EVERY action:                                    │
│  □ Did I observe the result?                            │
│  □ Did I plan the next action?                          │
│  □ Did I execute immediately?                           │
│                                                         │
│  Before reporting:                                      │
│  □ Is this a milestone?                                 │
│  □ Would silence be better for flow?                    │
│                                                         │
│  When stuck:                                            │
│  □ Did I try all verb classes?                          │
│  □ Did I examine all nouns?                             │
│  □ Did I check inventory?                               │
│                                                         │
│  When in danger:                                        │
│  □ Did I prioritize survival?                           │
│  □ Did I execute escape/recovery?                       │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## Related References

- `references/survival.md` - Detailed self-healing sequences
- `references/anti-stall.md` - Breaking out of loops
- `references/reporting-style.md` - Milestone definitions
- `references/mode-switching.md` - Puzzle mode for complex situations