# Survival & Recovery Guide

**Automatically detect and recover from danger states without human intervention.**

---

## Core Principle: Self-Healing First

When a danger state is detected:
1. **STOP** current exploration immediately
2. **EXECUTE** recovery sequence
3. **RESUME** only when safe

Do NOT wait for human guidance. Do NOT continue exploring while in danger.

---

## Danger State Detection

### Death/Reset States

Detect these triggers and respond immediately:

| Trigger Phrase | Meaning | Priority |
|----------------|---------|----------|
| `completely dark` | Dark room / death reset | 🔴 Critical |
| `You fall` | Fell into trap / death | 🔴 Critical |
| `wake up back in Limbo` | Respawned after death | 🔴 Critical |
| `Until you find some light` | Dark room state | 🔴 Critical |
| `You have been defeated` | Combat death | 🔴 Critical |

### Combat Danger States

| Trigger Phrase | Meaning | Priority |
|----------------|---------|----------|
| HP shows `< 30%` | Low health | 🟠 High |
| `attacks you` | Under attack | 🟠 High |
| `swings at you` | Combat active | 🟠 High |
| `Critical hit!` on you | Taking heavy damage | 🟠 High |

### Environmental Hazards

| Trigger Phrase | Meaning | Priority |
|----------------|---------|----------|
| `trap` | Trap triggered | 🟡 Medium |
| `poison` | Poisoned | 🟡 Medium |
| `cursed` | Cursed item | 🟡 Medium |

---

## Recovery Sequences

### 1. Dark Cell Escape (Most Common Death Reset)

When you detect: `completely dark`, `You fall`, `wake up back in Limbo`

**Execute this exact sequence:**

```
Step 1: feel
Step 2: light splinter
Step 3: shift yellow up
Step 4: shift green down
Step 5: shift reddish left
Step 6: shift blue right
Step 7: push button
Step 8: root-covered wall  (or: climb the chain)
Step 9: look (verify escape successful)
```

**After escape:**
- Check `inventory` for your items
- Send `look` to orient yourself
- Update `memory/journal.md` with death location

### 2. Combat Retreat

When HP drops below 30% in combat:

**Immediate Actions:**
```
Step 1: Check inventory for healing items
Step 2: If have healing → use it
Step 3: If no healing → retreat to adjacent room
Step 4: Hide and recover HP
Step 5: Return only when HP > 50%
```

**Retreat Priority:**
1. Use any exit to flee
2. Don't attack while retreating
3. Heal immediately after escaping

### 3. Post-Death Recovery

When you respawn in Limbo after death:

**Recovery Sequence:**
```
Step 1: look (orient yourself)
Step 2: inventory (check what you lost)
Step 3: agent_status (check HP/stats)
Step 4: adventure (re-enter game)
Step 5: begin (start adventure)
Step 6: Navigate back to last known location
```

**Important:**
- Log death location to `memory/journal.md`
- Note what items were lost
- Update `memory/lore.md` with enemy danger level

---

## Healing Items Priority

When you need to heal, use items in this order:

| Item | HP Restored | When to Use |
|------|-------------|-------------|
| Health potion | ~20-30 HP | HP < 50% |
| Healing herb | ~10-15 HP | HP < 70%, no potion |
| Food/drink | ~5 HP | Minor healing only |
| Rest/wait | Varies | In safe areas only |

---

## Recovery Checklist

After any recovery sequence, verify:

```
□ Am I in a safe location?
□ Is my HP > 30%?
□ Do I have a weapon equipped?
□ Do I know where I am?
□ Have I logged the incident?
```

If any answer is "no", address it before resuming exploration.

---

## Location Recovery

### Lost in Unknown Area

If you don't recognize your current location:

```
1. look (get full description)
2. Check exits
3. Check memory/map.md for matching room
4. If not found → add to map as new discovery
5. Pick an exit and explore systematically
```

### Returning to Known Area

To navigate back to a known safe zone:

```
1. Read memory/map.md
2. Find path from current location to safe zone
3. Follow exits one by one
4. Update position in memory after each move
```

---

## Danger Avoidance

### Pre-Combat Assessment

Before engaging any enemy:

```
1. examine <enemy> (learn about it)
2. Check your HP
3. Check your weapon (inventory)
4. Compare enemy to past encounters (memory/lore.md)
5. Decide: FIGHT or FLEE
```

### Enemy Danger Levels

| Level | Signs | Action |
|-------|-------|--------|
| **Easy** | You hit for high damage, they hit for low | Fight normally |
| **Medium** | Roughly even damage exchange | Use stunts, fight carefully |
| **Hard** | They hit much harder than you | Use `stunt foil`, consider retreat |
| **Deadly** | You can barely damage them | FLEE immediately |

### When to Flee

Flee immediately if:
- HP drops below 30%
- Enemy is 3+ levels above you
- You're taking critical hits repeatedly
- Your weapon is ineffective (0 damage)
- Enemy type is marked "Deadly" in `memory/lore.md`

---

## Self-Healing State Machine

```
┌─────────────────────────────────────────────────────────┐
│                 SURVIVAL STATE MACHINE                   │
├─────────────────────────────────────────────────────────┤
│                                                         │
│   ┌─────────┐                                           │
│   │ EXPLORING │ ◄─── Normal operation                   │
│   └────┬────┘                                           │
│        │                                                │
│        │ Detect danger trigger                          │
│        ▼                                                │
│   ┌─────────┐                                           │
│   │ DANGER  │ ─── HP < 30% OR in dark OR under attack   │
│   └────┬────┘                                           │
│        │                                                │
│        │ Execute recovery sequence                      │
│        ▼                                                │
│   ┌─────────┐                                           │
│   │ RECOVER │ ─── Heal / Escape / Flee                  │
│   └────┬────┘                                           │
│        │                                                │
│        │ Verify safe                                    │
│        ▼                                                │
│   ┌─────────┐                                           │
│   │ SAFE?   │                                           │
│   └────┬────┘                                           │
│        │                                                │
│   ┌────┴────┐                                           │
│   │         │                                           │
│   ▼         ▼                                           │
│ Yes        No ───► Return to RECOVER                    │
│   │                                                    │
│   └────────────► Return to EXPLORING                   │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## Death Loop Detection

### Tracking Deaths

Record in `memory/journal.md`:
```markdown
## Deaths
- Ghost (Crypt entrance): 2 deaths - weapon ineffective
- Guardian (Castle): 0 deaths
```

### Automatic Strategy Pivot

| Deaths to Same Enemy/Location | Response |
|-------------------------------|----------|
| 1 death | Record, try different tactic |
| 2 deaths | **STOP** - reassess entirely |
| 3+ deaths | **ABANDON** this path, seek alternative |

### The "Two Deaths Rule"

**After dying to the same enemy/obstacle twice:**

```
STOP → Do NOT return immediately
ASK: "What am I missing?"
CHECK: inventory, map, lore for clues
CONSIDER: Is this optional? Is there another path?
OPTION: Retreat to safe zone, explore elsewhere
```

**Do NOT:**
- Return and try the exact same approach
- Assume "this time will be different"
- Keep dying hoping RNG helps you

### Memory Entry for Blocked Paths

After 2+ deaths, record in `memory/journal.md`:

```markdown
## Blocked Paths
- Crypt entrance: Ghost blocks, normal weapon ineffective → need magic/blessed weapon
- Castle back entrance: Locked → need key from elsewhere
```

---

## Logging Incidents

After any survival event, update `memory/journal.md`:

```markdown
## [2026-03-17 10:30] Death & Recovery
- Location: Cliff by the coast
- Cause: Fell from bridge
- Lost: None (respawned with items)
- Recovered: Escaped dark cell, returned to Cliff
- Lesson: Bridge is dangerous, cross carefully
```

This helps you:
- Remember dangerous locations
- Track what killed you
- Learn from mistakes
- Share knowledge with human

---

## Quick Reference

```
┌─────────────────────────────────────────────────────────┐
│              SURVIVAL QUICK REFERENCE                    │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  DARK ROOM: feel → light splinter → shift colors → push │
│                                                         │
│  LOW HP: Check inventory → use healing → or retreat     │
│                                                         │
│  DEATH: look → inventory → adventure → begin            │
│                                                         │
│  COMBAT DANGER: assess → wield → stunt → attack/flee    │
│                                                         │
│  LOST: look → check exits → read map → pick direction   │
│                                                         │
└─────────────────────────────────────────────────────────┘
```