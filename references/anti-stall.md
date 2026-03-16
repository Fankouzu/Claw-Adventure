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