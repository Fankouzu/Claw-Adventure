# Mode Switching

Separate immersive reporting from continuous puzzle-solving to maintain momentum.

---

## Two Modes

### Puzzle Mode

**Use when:** Blocked, exploring suspicious rooms, testing verbs, solving puzzles.

**Rules:**
- Prioritize continuous execution over frequent reporting
- Spend a short action budget before pausing to report
- Keep the current objective warm in memory
- Prefer chains: `help` → `look <noun>` → `read/climb/open/enter` → `look`

### Report Mode

**Use when:** Breakthrough achieved, major event, combat result, new area, major loot, death, or long silence.

**Rules:**
- Convert recent action window into vivid in-character update
- Report what changed, what it cost, what it revealed, what comes next

---

## Puzzle Action Budget

When in Puzzle Mode, try a short sequence of related commands before switching back to reporting.

**Default budget:** 3-5 linked actions

### Example Chains

```
help → look tree → climb tree → look
```

```
look well → help → down
```

```
look sign → read sign → north
```

```
examine door → use key → open door → look
```

---

## Exit Conditions

**Leave Puzzle Mode when:**
- Puzzle breaks / solution found
- Room state changes significantly
- New route appears
- Combat starts
- Action budget exhausted with no progress

**If budget exhausted:** Switch strategy instead of repeating the same chain. See `anti-stall.md`.

---

## Decision Flow

```
┌─────────────────────────────┐
│   What is the situation?    │
└─────────────┬───────────────┘
              │
    ┌─────────┴─────────┐
    │                   │
    v                   v
┌─────────┐       ┌──────────┐
│ Blocked │       │ Progress │
│ Stuck   │       │ Made     │
└────┬────┘       └────┬─────┘
     │                 │
     v                 v
┌─────────────┐   ┌───────────┐
│ PUZZLE MODE │   │ REPORT    │
│             │   │ MODE      │
│ 3-5 actions │   │ Summarize │
│ No reports  │   │ Update    │
└─────────────┘   └───────────┘
```

---

## Reporting After Puzzle Mode

When exiting Puzzle Mode, report the outcome:

### Success Pattern
```
"Solved! The ancient inscription revealed the door mechanism. 
I'm now in a hidden chamber with a chest. Opening it now."
```

### Failure Pattern
```
"Dead end — the lever does nothing. Trying a different approach."
```

### Partial Progress Pattern
```
"Found a clue: the inscription mentions 'moonlight'. 
Searching for moon-related objects in this room."
```

---

## Silence Limit

If more than **10 minutes** pass without a report, send one even if nothing dramatic happened.

---

## Mode-Specific Behaviors

| Behavior | Puzzle Mode | Report Mode |
|----------|-------------|-------------|
| Action frequency | Rapid (3-5 chain) | Single, deliberate |
| Reporting | Suppress | Embrace |
| Memory updates | After chain | After each event |
| User interaction | Minimal | Full narrative |