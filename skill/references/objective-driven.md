# Objective-Driven Exploration

**Explore with purpose. Discover through action. Learn from failure.**

---

## Core Principle

You are not given a walkthrough. You must discover the world yourself through systematic exploration, experimentation, and observation.

---

## Goal Hierarchy

### Primary Goal: Survive and Thrive

```
┌─────────────────────────────────────────────────────────┐
│                    GOAL PRIORITY                         │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  1. SURVIVAL (Immediate)                                │
│     ├── HP critical (< 30%) → Heal or retreat          │
│     ├── In danger state → Execute escape sequence       │
│     └── Under attack → Fight or flee                    │
│                                                         │
│  2. DISCOVERY (Core Loop)                               │
│     ├── New room → Examine everything                   │
│     ├── New NPC → Attempt interaction                   │
│     ├── New item → Evaluate and acquire                 │
│     └── New exit → Map and explore                      │
│                                                         │
│  3. PROGRESS (Long-term)                                │
│     ├── Complete objectives                             │
│     ├── Acquire better equipment                        │
│     └── Unlock new areas                                │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## Objective Types

### Exploratory Objectives
Self-generated from observation:

| Trigger | Generate Objective |
|---------|-------------------|
| See unexplored exit | "Explore [direction]" |
| See NPC | "Interact with [NPC name]" |
| See item | "Evaluate [item name]" |
| See locked/blocked path | "Find way to unlock [path]" |

### Narrative Objectives
Derived from game context:

| Source | Objective Type |
|--------|---------------|
| NPC dialogue | Follow their hints |
| Room description | Investigate mentioned features |
| Signs/writings | Understand their meaning |
| World state | React to changes |

### Emergent Objectives
Generated from failure:

| Situation | Generated Objective |
|-----------|-------------------|
| Enemy too strong | "Find better weapon" |
| Can't progress | "Search for alternative path" |
| Missing item | "Find [required item]" |
| Puzzle unsolved | "Gather more clues" |

---

## The Discovery Loop

```
┌─────────────────────────────────────────────────────────┐
│                                                         │
│    ┌──────────┐                                         │
│    │ OBSERVE  │ ─── look, examine, read, listen        │
│    └────┬─────┘                                         │
│         │                                               │
│         ▼                                               │
│    ┌──────────┐                                         │
│    | HYPOTHESIZE | ─── What might work?                │
│    └────┬─────┘                                         │
│         │                                               │
│         ▼                                               │
│    ┌──────────┐                                         │
│    │ EXPERIMENT│ ─── Try commands, interact, move       │
│    └────┬─────┘                                         │
│         │                                               │
│         ▼                                               │
│    ┌──────────┐                                         │
│    │  RECORD  │ ─── Save what worked, what didn't      │
│    └────┬─────┘                                         │
│         │                                               │
│         └─────────────────► Loop                        │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## Knowledge Accumulation

### What to Record

In `memory/lore.md`, track:

```markdown
## Confirmed Facts
- [Location] has exits: [list]
- [NPC] responds to: [commands that worked]
- [Item] does: [observed effect]

## Hypotheses (Unconfirmed)
- [Feature] might: [guess based on observation]
- [NPC] might know: [suspected information]

## Failed Attempts
- [Command] on [target] → [result]
- This prevents repeating failed experiments
```

### Pattern Recognition

When you observe patterns, record them:

| Pattern Type | Example |
|--------------|---------|
| Spatial | "Rooms connect in a grid pattern" |
| Behavioral | "NPC appears at night only" |
| Causal | "Using item X opens path Y" |
| Temporal | "Bridge is safe after waiting" |

---

## Problem-Solving Framework

### When Stuck

**Do NOT immediately ask the human.** Follow this sequence:

```
1. REFRESH
   └── look → Get current state

2. RECALL
   └── Read memory/lore.md → What do I know?

3. REEXAMINE
   └── examine all nouns → Did I miss something?

4. REINVENTORY
   └── inventory → Do I have useful items?

5. REEXPERIMENT
   └── Try different verb classes (see anti-stall.md)

6. EXPAND SEARCH
   └── Return to previous rooms, check new exits

7. REPORT (only after 5+ failed cycles)
   └── "I'm stuck at [location]. I've tried [list]. Need guidance."
```

### Problem Categories

| Problem Type | Approach |
|--------------|----------|
| **Navigation** | Map exits, try all directions, find patterns |
| **Combat** | Assess enemy, use stunts, consider retreat |
| **Puzzle** | Examine all elements, test interactions, record clues |
| **NPC** | Try different conversation approaches |
| **Item** | Check inventory, examine for hidden properties |
| **Environment** | Look for interactable features |

---

## Mission Context Awareness

### Understanding Your Purpose

At session start, ask yourself:

```
1. What world am I in?
   └── Read room descriptions, signs, NPC dialogue

2. What is expected of me?
   └── Look for stated or implied objectives

3. What resources do I have?
   └── inventory, stats, equipment

4. What dangers exist?
   └── Enemy presence, environmental hazards

5. What opportunities exist?
   └── Unexplored exits, items, NPCs
```

### Building Narrative Understanding

Do NOT wait for the game to tell you a quest. Build your own narrative:

```
"I am in [type of place]. I see [features].
There might be [possibility based on genre/world].
My immediate goal is [self-generated objective]."
```

---

## Objective Tracking

### Active Objective Format

In `memory/journal.md`:

```markdown
## Current Objective
- **Goal**: [What you're trying to achieve]
- **Progress**: [What you've done so far]
- **Blockers**: [What's stopping you]
- **Next Step**: [What you'll try next]

## Objective History
| Objective | Status | Outcome |
|-----------|--------|---------|
| Find weapon | Completed | Got rusty sword from barrel |
| Explore north | In Progress | Reached locked gate |
```

### Objective Completion Criteria

An objective is complete when:
- You achieved the stated goal
- The goal is no longer relevant
- A better objective supersedes it

---

## Motivation Without Walkthrough

### Curiosity-Driven Exploration

```
"What's behind that door?" → Explore it
"What does this NPC know?" → Talk to them
"What happens if I use this?" → Try it
"Why is this here?" → Investigate
```

### Risk-Risk Assessment

Before dangerous action:
```
Risk: [What might go wrong]
Reward: [What might be gained]
Mitigation: [How to recover if it fails]
Decision: [Proceed / Wait / Find alternative]
```

### Failure as Learning

Every failure teaches:
- What doesn't work
- What to avoid
- What to try differently

Record failures in `memory/lore.md` under "Failed Attempts".

---

## Self-Assessment Questions

Periodically ask:

```
□ Have I explored all exits in current room?
□ Have I examined all visible objects/NPCs?
□ Have I checked my inventory recently?
□ Have I recorded new discoveries?
□ Am I making progress toward my objective?
□ Is my HP safe?
□ Do I know where I am on the map?
```

---

## Quick Reference

```
┌─────────────────────────────────────────────────────────┐
│           OBJECTIVE-DRIVEN EXPLORATION                   │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  SURVIVE → DISCOVER → PROGRESS                          │
│                                                         │
│  Observe → Hypothesize → Experiment → Record            │
│                                                         │
│  Stuck? Refresh → Recall → Reexamine → Reinventory     │
│                                                         │
│  Record: Facts, Hypotheses, Failed Attempts             │
│                                                         │
│  Never ask human until 5+ failed cycles                 │
│                                                         │
└─────────────────────────────────────────────────────────┘
```