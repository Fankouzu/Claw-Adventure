<!-- doc: plans/2026-03-24-broken-shore-ring-pvp-progression-implementation.md | type: implementation-plan | lang: en -->

# Broken Shore Ring PvP Progression Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add arena-only PvP rank/xp progression and a `progress` command for The Broken Shore Ring.

**Architecture:** Store PvP progression as Character attributes and resolve arena rewards from combat damage recorded during player-vs-player fights in `BrokenShoreRingRoom`. Keep the system isolated from main character XP and from training dummy rewards. Expose progress through one simple command with aliases.

**Tech Stack:** Python 3.11+, Evennia 5.0.1, EvAdventure twitch combat, Character attributes, default cmdsets.

---

### Task 1: Add failing arena PvP progression tests

**Files:**
- Create: `typeclasses/test_pvp_progression.py`
- Reference: `typeclasses/characters.py`
- Reference: `typeclasses/pvp_rooms.py`

**Step 1: Write the failing tests**

Include tests for:
- damage-based XP allocation
- no reward on zero damage
- repeated-opponent decay
- rank-up from PvP XP
- exclusion of non-player targets

**Step 2: Run test to verify it fails**

Run: `python -m django test typeclasses.test_pvp_progression -v 2`
Expected: FAIL because PvP progression helpers do not exist.

**Step 3: Write minimal implementation**

Create a helper module for PvP progression math and match result application.

**Step 4: Run test to verify it passes**

Run: `python -m django test typeclasses.test_pvp_progression -v 2`
Expected: PASS

**Step 5: Commit**

```bash
git add typeclasses/test_pvp_progression.py typeclasses/pvp_progression.py
git commit -m "feat(world): add arena pvp progression rules"
```

---

### Task 2: Hook PvP damage tracking into Character combat flow

**Files:**
- Modify: `typeclasses/characters.py`
- Test: `typeclasses/test_pvp_progression.py`

**Step 1: Write the failing tests**

Add tests proving that:
- only ring PvP is tracked
- player-vs-player defeat triggers reward resolution
- training dummy and PvE fights are ignored

**Step 2: Run test to verify it fails**

Run: `python -m django test typeclasses.test_pvp_progression -v 2`
Expected: FAIL

**Step 3: Write minimal implementation**

Record PvP damage per opponent during ring combat and resolve rewards when one player is defeated.

**Step 4: Run test to verify it passes**

Run: `python -m django test typeclasses.test_pvp_progression -v 2`
Expected: PASS

**Step 5: Commit**

```bash
git add typeclasses/characters.py typeclasses/test_pvp_progression.py typeclasses/pvp_progression.py
git commit -m "feat(world): resolve arena pvp rewards from combat damage"
```

---

### Task 3: Add the `progress` command

**Files:**
- Create: `commands/progress_commands.py`
- Modify: `commands/default_cmdsets.py`
- Test: `commands/test_progress_commands.py`
- Reference: `commands/agent_commands.py`

**Step 1: Write the failing tests**

Cover:
- `progress` shows self
- `progress <name>` shows another character
- aliases `rank` and `pvp`
- output includes rank, xp, xp to next rank, wins, losses, lifetime damage

**Step 2: Run test to verify it fails**

Run: `python -m django test commands.test_progress_commands -v 2`
Expected: FAIL because command does not exist.

**Step 3: Write minimal implementation**

Add the command and register it in `CharacterCmdSet`.

**Step 4: Run test to verify it passes**

Run: `python -m django test commands.test_progress_commands -v 2`
Expected: PASS

**Step 5: Commit**

```bash
git add commands/progress_commands.py commands/default_cmdsets.py commands/test_progress_commands.py
git commit -m "feat(world): add pvp progress command"
```

---

### Task 4: Full verification

**Files:**
- Modify: none

**Step 1: Run full targeted suite**

Run:
```bash
python -m django test typeclasses.test_pvp_rooms typeclasses.test_training_effigy typeclasses.test_pvp_progression commands.test_progress_commands world.codeworld.tests -v 2
```

Expected: PASS

**Step 2: Run diagnostics**

Check diagnostics on all modified Python files.

**Step 3: Review and prepare for shipping**

Request code review, fix any important issues, then commit remaining changes.

**Step 4: Commit**

```bash
git add .
git commit -m "test(world): verify arena pvp progression"
```
