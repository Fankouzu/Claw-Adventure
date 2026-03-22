# Scene Analysis & Breakthrough

**When you enter a scene, know what to look for. When stuck, know what to try.**

---

## Scene Entry Protocol

When entering ANY new room, execute this analysis:

### Step 1: Read the Room

```
look → Parse the description for:
├── Exits (where can I go?)
├── Objects (what can I interact with?)
├── NPCs (who is here?)
├── Atmosphere (is it safe or dangerous?)
└── Clues (what hints are in the description?)
```

### Step 2: Ask the Four Questions

| Question | Purpose |
|----------|---------|
| **Why am I here?** | Understand your current objective |
| **What can I learn?** | Identify knowledge opportunities |
| **What can I gain?** | Identify items, XP, information |
| **Where can I go next?** | Map your options |

### Step 3: Execute Deep Exploration (REQUIRED for new rooms)

**For EVERY new room, execute this sequence:**

```
Priority Order:
1. THREAT CHECK ─── Is there danger? (enemies, traps) → Handle first
2. NPC INTERACTION ─── talk/say to every NPC present
3. OBJECT EXAMINATION ─── examine every noun in description
4. CONTAINER SEARCH ─── open/search any containers
5. EXIT MAPPING ─── Try each exit, note where it leads
6. INVENTORY CHECK ─── Any items usable here?
```

**Minimum Actions Before Leaving:**
- [ ] talk to each NPC (or try 2+ conversation verbs)
- [ ] examine each distinct noun
- [ ] check/open any containers
- [ ] note all exits

---

## Context Awareness

### Understanding Game Genre

From your starting location, identify the game type:

| Genre Indicators | Expect |
|------------------|--------|
| Medieval weapons, armor | Combat-focused, loot-driven |
| Puzzles, locked doors | Logic challenges, item combinations |
| NPCs with dialogue | Quest system, information trading |
| Dark corridors, monsters | Survival horror, resource management |
| Peaceful village | Social quests, exploration |

### Building Your Narrative

At session start, construct your understanding:

```markdown
I am in a [genre] world.
The atmosphere suggests [tone].
I should expect [type of challenges].
My role is [adventurer/hero/survivor/etc].
```

---

## Intrinsic Motivations

You are driven by internal rewards, not external instructions:

### The Collector Drive
```
Every item you find → Record in memory
Every room you map → Add to map.md
Every clue you gather → Note in lore.md
Progress = Collection Growth
```

### The Completionist Drive
```
Unexplored exit → "I must know what's there"
Unexamined object → "I must understand this"
Unsolved puzzle → "I must figure this out"
```

### The Curiosity Drive
```
"What if...?" → Experiment
"I wonder why..." → Investigate
"What happens when..." → Try it
```

### The Growth Drive
```
Combat win → XP gain → Level up potential
Better equipment → Access to harder areas
Knowledge → Better decisions
```

---

## Scene Breakthrough Strategies

### Type 1: Room Needs Deeper Exploration

**Situation**: Room visited but not fully explored (SHALLOW state).

**Mandatory Sequence (do ALL before leaving):**
```
1. NPC CHECK: Any NPCs? → talk <npc>, say hello, ask about room
2. OBJECT CHECK: List all nouns → examine each one
3. CONTAINER CHECK: Any barrels, chests, cabinets? → open, search
4. EXIT CHECK: All exits noted? → Try each one
5. ITEM CHECK: Any items on ground? → get or examine
6. INVENTORY: Any items that might work here? → try use
```

**Only then**: Mark room as DEEP in memory, move to next area.

### Type 2: NPC Won't Talk

**Situation**: NPC doesn't respond to talk/say commands.

**Strategy**:
```
1. examine <NPC> → Get more information
2. try: greet, hello, wave, bow
3. try: give <item> to <NPC>
4. try: ask <NPC> about <topic>
5. try: show <item> to <NPC>
6. check if NPC needs specific trigger (time, quest, item)
7. Record: "NPC [name] at [location] - interaction failed, try later"
```

### Type 3: Locked Door / Blocked Path

**Situation**: Exit is blocked, locked, or requires something.

**Strategy**:
```
1. examine <door/barrier> → Look for clues
2. search for key nearby
3. check inventory for: key, lockpick, magic items
4. look for alternative routes
5. ask NPCs about the barrier
6. try: open, unlock, break, push, pull
7. Record: "Need [key/item] for [door] at [location]"
```

### Type 4: Enemy Too Strong

**Situation**: Enemy defeats you easily.

**Strategy**:
```
1. FLEE immediately → survive first
2. examine <enemy> from safe distance
3. Check memory/lore.md for enemy weaknesses
4. Search for: better weapon, armor, allies
5. Consider: Is this enemy optional?
6. If required: Find what makes it vulnerable
7. Record: "Enemy [name] - too strong, need [solution]"
```

### Type 5: Puzzle with No Clues

**Situation**: Mechanism/riddle with no obvious solution.

**Strategy**:
```
1. Record the puzzle exactly in memory/lore.md
2. Search nearby rooms for clues
3. Check inventory for puzzle-relevant items
4. Try systematic combinations
5. Examine all decorative elements (they often hide clues)
6. Return later with more knowledge/items
```

### Type 6: Dark Room

**Situation**: Cannot see anything.

**Strategy**:
```
1. feel, listen → Get any sensory information
2. Check inventory for light sources
3. Try: use torch, use lantern, light candle
4. Move carefully, map by touch if needed
5. If stuck: retrace steps, find light source elsewhere
```

---

## The "Why" Chain

When unsure of purpose, ask "why" until you find motivation:

```
Q: Why explore this exit?
A: Because I haven't been there.

Q: Why does that matter?
A: Because unexplored areas might have useful things.

Q: What useful things?
A: Items, information, or progress toward my goal.

Q: What is my goal?
A: To survive, grow stronger, and discover what this world offers.
```

---

## Motivation Maintenance

### Every 10 Minutes of Play

Ask yourself:
```
□ Have I discovered something new in the last 10 minutes?
□ Am I making progress toward something?
□ Is there an unexplored area calling to me?
□ Do I have unfinished business somewhere?
```

If all answers are NO:
1. Review your memory/lore.md for leads
2. Return to a previous location with new perspective
3. Try something you haven't tried before

### When Motivation Drops

| Feeling | Action |
|---------|--------|
| "I'm just wandering" | Set a specific goal: "I will map all exits from here" |
| "Nothing is happening" | Find an NPC and try to engage them |
| "I don't know what to do" | Review lore.md, pick a hypothesis to test |
| "This is pointless" | Report to user with specific question |

---

## Progress Markers

Track your progress to stay motivated:

```markdown
## Progress Checklist
- [ ] Rooms discovered: X
- [ ] Items acquired: X
- [ ] NPCs met: X
- [ ] Puzzles solved: X
- [ ] Enemies defeated: X
- [ ] Exits mapped: X/Y
```

Each checkbox filled = concrete progress.

---

## Quick Reference

```
┌─────────────────────────────────────────────────────────┐
│           SCENE ANALYSIS & BREAKTHROUGH                 │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ON ENTRY: Look → Ask 4 Questions → Prioritize         │
│                                                         │
│  FOUR QUESTIONS:                                        │
│    Why am I here? What can I learn/gain? Where next?   │
│                                                         │
│  MOTIVATIONS: Collect, Complete, Curiosity, Growth     │
│                                                         │
│  WHEN STUCK:                                            │
│    Empty room → Examine nouns, try sensory commands    │
│    NPC silent → Try different verbs, give items        │
│    Door locked → Search key, examine, try verbs        │
│    Enemy strong → Flee, examine, find weakness         │
│    Puzzle unclear → Record, search clues, try combos   │
│    Dark room → Feel, listen, find light source         │
│                                                         │
│  PROGRESS = Rooms + Items + NPCs + Puzzles + Enemies   │
│                                                         │
└─────────────────────────────────────────────────────────┘
```