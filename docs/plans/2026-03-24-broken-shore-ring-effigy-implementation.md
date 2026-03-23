# Broken Shore Ring Effigy Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add The Salt-Worn Sparring Effigy to The Broken Shore Ring as a combat-capable training target that grants capped real Character XP on defeat only, with enough lifetime headroom to reach at least level 2.

**Architecture:** Implement a dedicated training dummy typeclass plus a small XP reward helper. Place the dummy into the arena through `world/codeworld/definitions.py`, and keep reward logic isolated from the existing PvE achievement/loot flow. Persist daily/lifetime training usage on the Character so the feature survives reconnects and deploys.

**Tech Stack:** Python 3.11+, Evennia 5.0.1, EvAdventure combat, Django/Evennia persistence, code-defined world sync.

---

### Task 1: Add failing reward-rule tests

**Files:**
- Create: `typeclasses/test_training_effigy.py`
- Reference: `typeclasses/characters.py`
- Reference: `typeclasses/mobs.py`

**Step 1: Write the failing tests**

```python
class TestTrainingEffigyRewards(EvenniaTest):
    def test_level_one_defeat_grants_25_xp(self):
        ...

    def test_level_six_defeat_grants_no_xp(self):
        ...

    def test_daily_cap_limits_award(self):
        ...

    def test_lifetime_cap_limits_award(self):
        ...
```

**Step 2: Run test to verify it fails**

Run: `python -m django test typeclasses.test_training_effigy.TestTrainingEffigyRewards -v 2`
Expected: FAIL because the effigy typeclass / reward helper do not exist.

**Step 3: Write minimal implementation**

Create the smallest reward helper and dummy defeat hook needed to satisfy the tests.

**Step 4: Run test to verify it passes**

Run: `python -m django test typeclasses.test_training_effigy.TestTrainingEffigyRewards -v 2`
Expected: PASS

**Step 5: Commit**

```bash
git add typeclasses/test_training_effigy.py typeclasses/training.py typeclasses/training_dummy.py
git commit -m "feat(world): add capped training dummy reward rules"
```

---

### Task 2: Add defeat/reset behavior and English player messages

**Files:**
- Modify: `typeclasses/training_dummy.py`
- Test: `typeclasses/test_training_effigy.py`

**Step 1: Write the failing tests**

```python
def test_dummy_defeat_does_not_log_standard_combat_achievement(self):
    ...

def test_dummy_defeat_uses_english_cap_message(self):
    ...

def test_dummy_recovers_after_defeat(self):
    ...
```

**Step 2: Run test to verify it fails**

Run: `python -m django test typeclasses.test_training_effigy -v 2`
Expected: FAIL

**Step 3: Write minimal implementation**

Implement:
- no-loot/no-achievement isolation
- English-only reward/cap text
- dummy reset after defeat

**Step 4: Run test to verify it passes**

Run: `python -m django test typeclasses.test_training_effigy -v 2`
Expected: PASS

**Step 5: Commit**

```bash
git add typeclasses/training_dummy.py typeclasses/test_training_effigy.py
git commit -m "feat(world): add ring training dummy defeat flow"
```

---

### Task 3: Place the dummy in the arena through codeworld

**Files:**
- Modify: `world/codeworld/definitions.py`
- Modify: `world/codeworld/tests.py`

**Step 1: Write the failing test**

```python
def test_broken_shore_ring_contains_salt_worn_sparring_effigy(self):
    ...
```

**Step 2: Run test to verify it fails**

Run: `python -m django test world.codeworld.tests.BrokenShoreRingDefinitionsTest -v 2`
Expected: FAIL

**Step 3: Write minimal implementation**

Add a `CODED_THINGS` entry for the dummy inside `Claw / The Broken Shore Ring`.

**Step 4: Run test to verify it passes**

Run: `python -m django test world.codeworld.tests.BrokenShoreRingDefinitionsTest -v 2`
Expected: PASS

**Step 5: Commit**

```bash
git add world/codeworld/definitions.py world/codeworld/tests.py
git commit -m "feat(world): place training effigy in broken shore ring"
```

---

### Task 4: Verification

**Files:**
- Modify: none

**Step 1: Run targeted Django tests**

Run:
```bash
python -m django test world.codeworld.tests.BrokenShoreRingDefinitionsTest typeclasses.test_pvp_rooms.TestBrokenShoreRingRoom typeclasses.test_training_effigy -v 2
```

Expected: PASS

**Step 2: Run diagnostics**

Check diagnostics on all changed Python files.

**Step 3: Sync local codeworld**

Run:
```bash
evennia sync_codeworld
```

Expected: dummy object appears in local world if room already exists.

**Step 4: Commit**

```bash
git add .
git commit -m "test(world): verify broken shore ring training effigy"
```
