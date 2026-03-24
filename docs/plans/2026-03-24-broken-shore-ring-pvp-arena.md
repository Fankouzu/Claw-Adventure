<!-- doc: plans/2026-03-24-broken-shore-ring-pvp-arena.md | type: implementation-plan | lang: en -->

# The Broken Shore Ring Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add a safe, incremental PvP arena called **The Broken Shore Ring** to Claw Adventure without destabilizing the existing tutorial world, Twitch combat flow, or PvE achievement systems.

**Architecture:** Build the feature in three isolated phases. V1 adds only a dedicated PvP room + world hookup using Evennia/EvAdventure’s native non-lethal PvP behavior. V2 adds consensual duel commands and attack gating. V3 adds PvP-specific persistence, points, and anti-abuse rules without overloading the current PvE combat log schema.

**Tech Stack:** Python 3.11+, Evennia 5.0.1, EvAdventure Twitch combat, Django models, code-defined world sync (`world/codeworld`), Evennia cmdsets/typeclasses.

---

## Scope and sequencing

- **V1 (recommended first release):** arena room + exit + non-lethal direct PvP + no-loot + room copy updates.
- **V2:** `challenge` / `accept` / `decline` flow and attack gating so direct PC attacks require consent.
- **V3:** PvP log model, arena points, leaderboard-ready queries, and abuse controls.

## Hard boundaries

- Do **not** change global room behavior in `typeclasses/rooms.py`.
- Do **not** reuse current PvE `CombatLog` for PvP opponent identity.
- Do **not** implement points, rankings, or anti-abuse in V1.
- Do **not** change frontend/API behavior until V3 requires it.

## Naming

- **Canonical English name:** `The Broken Shore Ring`
- **Recommended slug / key fragment:** `broken_shore_ring`
- **Reasoning:** `ring` carries a natural English combat/duel-space meaning without sounding like a formal sports arena. It fits a ruined circular fighting ground better than `arena`.

---

### Task 1: Create the V1 PvP room typeclass

**Files:**
- Create: `typeclasses/pvp_rooms.py`
- Test: `world/tests/test_pvp_rooms.py`
- Reference: `typeclasses/rooms.py`
- Reference: `typeclasses/characters.py`

**Step 1: Write the failing test**

```python
from django.test import TestCase


class PvPRoomTypeclassTest(TestCase):
    def test_broken_shore_ring_room_flags(self):
        from typeclasses.pvp_rooms import BrokenShoreRingRoom

        room = BrokenShoreRingRoom()
        self.assertTrue(hasattr(room, "allow_combat"))
        self.assertTrue(hasattr(room, "allow_pvp"))
```

**Step 2: Run test to verify it fails**

Run: `python manage.py test world.tests.test_pvp_rooms.PvPRoomTypeclassTest -v 2`
Expected: FAIL with import error for `typeclasses.pvp_rooms`

**Step 3: Write minimal implementation**

```python
from evennia.contrib.tutorials.evadventure.rooms import EvAdventurePvPRoom


class BrokenShoreRingRoom(EvAdventurePvPRoom):
    """Dedicated non-lethal arena room for direct PvP in V1."""
```

Add room footer text that clearly states:
- PvP is enabled here
- combat is non-lethal
- defeated players cannot be looted
- V1 allows direct attack without challenge flow

**Step 4: Run test to verify it passes**

Run: `python manage.py test world.tests.test_pvp_rooms.PvPRoomTypeclassTest -v 2`
Expected: PASS

**Step 5: Commit**

```bash
git add typeclasses/pvp_rooms.py world/tests/test_pvp_rooms.py
git commit -m "feat: add broken shore ring pvp room typeclass"
```

---

### Task 2: Add V1 world definitions for The Broken Shore Ring

**Files:**
- Modify: `world/codeworld/definitions.py`
- Test: `world/tests/test_codeworld_definitions.py`
- Reference: `world/codeworld/README.md`
- Reference: `docs/evennia-tutorial-walkthrough.md`

**Step 1: Write the failing test**

```python
from django.test import SimpleTestCase
import world.codeworld.definitions as defs


class BrokenShoreRingDefinitionsTest(SimpleTestCase):
    def test_broken_shore_ring_room_exists(self):
        self.assertTrue(
            any(room["key"] == "Claw / The Broken Shore Ring" for room in defs.CODED_ROOMS)
        )
```

**Step 2: Run test to verify it fails**

Run: `python manage.py test world.tests.test_codeworld_definitions.BrokenShoreRingDefinitionsTest -v 2`
Expected: FAIL because room definition is missing

**Step 3: Write minimal implementation**

Add one room and one safe return exit in `world/codeworld/definitions.py`:

```python
{
    "key": "Claw / The Broken Shore Ring",
    "aliases": ["broken shore ring", "shore ring", "ring"],
    "typeclass": "typeclasses.pvp_rooms.BrokenShoreRingRoom",
    "desc": "<final arena room text>",
}
```

Use a **single explicit exit** back to a non-PvP room. Pick the destination only after confirming the exact tutorial/post-gatehouse room key from DB or world docs.

**Step 4: Run test to verify it passes**

Run: `python manage.py test world.tests.test_codeworld_definitions.BrokenShoreRingDefinitionsTest -v 2`
Expected: PASS

**Step 5: Commit**

```bash
git add world/codeworld/definitions.py world/tests/test_codeworld_definitions.py
git commit -m "feat: define broken shore ring world entry"
```

---

### Task 3: Verify V1 world sync locally

**Files:**
- Modify: none
- Test: runtime verification only
- Reference: `world/codeworld/README.md`

**Step 1: Run sync in local dev database**

Run: `evennia sync_codeworld`
Expected: output shows the new room and exit created or skipped idempotently

**Step 2: Verify created objects exist**

Run: `python scripts/list_evennia_objectdb_inventory.py --quiet --csv /tmp/broken_shore_ring.csv`
Expected: CSV contains `Claw / The Broken Shore Ring`

**Step 3: Verify typeclass and exit target**

Run: `python manage.py shell -c "from evennia import search_object; print(search_object('Claw / The Broken Shore Ring'))"`
Expected: one room object returned

**Step 4: Commit**

```bash
git add .
git commit -m "test: verify broken shore ring world sync"
```

---

### Task 4: Verify V1 direct PvP behavior manually

**Files:**
- Modify: none
- Test: manual in-game verification
- Reference: `typeclasses/characters.py`
- Reference: upstream EvAdventure PvP behavior

**Step 1: Start the server**

Run: `evennia start`
Expected: server boots cleanly

**Step 2: Move two test characters into the arena**

Use two local sessions or controlled puppets.

**Step 3: Verify direct PvP starts**

Command: `attack <other character>`
Expected:
- attack is allowed in the arena
- Twitch combat starts
- same command is still blocked outside PvP rooms

**Step 4: Verify defeat behavior**

Expected:
- defeated character is not permanently killed
- defeated character cannot be looted
- both characters remain usable after combat

**Step 5: Verify exit behavior**

Expected:
- leaving via the safe exit ends combat cleanly
- no lingering ghost combat state remains

**Step 6: Commit**

```bash
git add .
git commit -m "test: verify direct arena pvp behavior"
```

---

### Task 5: Add V2 duel commands and local state model

**Files:**
- Create: `commands/pvp_commands.py`
- Modify: `commands/default_cmdsets.py`
- Test: `world/tests/test_pvp_commands.py`
- Reference: `commands/default_cmdsets.py`

**Step 1: Write the failing tests**

```python
from django.test import TestCase


class PvPCommandsTest(TestCase):
    def test_challenge_requires_same_room(self):
        self.fail("implement same-room challenge test")

    def test_accept_expires_after_timeout(self):
        self.fail("implement timeout test")
```

**Step 2: Run test to verify it fails**

Run: `python manage.py test world.tests.test_pvp_commands.PvPCommandsTest -v 2`
Expected: FAIL

**Step 3: Write minimal implementation**

Implement:
- `challenge <target>`
- `accept <challenger>`
- `decline <challenger>`

Use temporary state only for V2:
- `caller.ndb.pvp_outgoing_challenge`
- `caller.ndb.pvp_incoming_challenge`
- timeout timestamp

Enforce:
- same room only
- target must be another PC
- target must also be in `BrokenShoreRingRoom`
- 60 second expiry
- challenge cleanup on decline/expiry

**Step 4: Add commands to the default character cmdset**

Modify `commands/default_cmdsets.py` to add the new PvP commands in `CharacterCmdSet` only.

**Step 5: Run test to verify it passes**

Run: `python manage.py test world.tests.test_pvp_commands.PvPCommandsTest -v 2`
Expected: PASS

**Step 6: Commit**

```bash
git add commands/pvp_commands.py commands/default_cmdsets.py world/tests/test_pvp_commands.py
git commit -m "feat: add consensual duel commands for arena"
```

---

### Task 6: Gate direct player-vs-player attacks behind V2 consent

**Files:**
- Modify: `typeclasses/characters.py`
- Modify: `typeclasses/pvp_rooms.py`
- Test: `world/tests/test_pvp_attack_gating.py`
- Reference: upstream EvAdventure Twitch combat command prechecks

**Step 1: Write the failing test**

```python
from django.test import TestCase


class PvPAttackGatingTest(TestCase):
    def test_direct_pc_attack_requires_acceptance_in_broken_shore_ring(self):
        self.fail("implement direct attack gating test")
```

**Step 2: Run test to verify it fails**

Run: `python manage.py test world.tests.test_pvp_attack_gating.PvPAttackGatingTest -v 2`
Expected: FAIL

**Step 3: Write minimal implementation**

Add a narrow hook that only affects PC-vs-PC combat in `BrokenShoreRingRoom`:
- if attacker and target are PCs in the arena
- and no accepted duel flag exists for that pair
- block the attack with a clear error message

Do **not** alter PvE combat elsewhere.

**Step 4: Run test to verify it passes**

Run: `python manage.py test world.tests.test_pvp_attack_gating.PvPAttackGatingTest -v 2`
Expected: PASS

**Step 5: Commit**

```bash
git add typeclasses/characters.py typeclasses/pvp_rooms.py world/tests/test_pvp_attack_gating.py
git commit -m "feat: require duel acceptance before arena pvp attacks"
```

---

### Task 7: Add V2 cleanup behavior for exits and disconnects

**Files:**
- Modify: `typeclasses/characters.py`
- Test: `world/tests/test_pvp_state_cleanup.py`

**Step 1: Write the failing tests**

```python
from django.test import TestCase


class PvPStateCleanupTest(TestCase):
    def test_leave_room_clears_duel_state(self):
        self.fail("implement leave-room cleanup test")

    def test_disconnect_clears_duel_state(self):
        self.fail("implement disconnect cleanup test")
```

**Step 2: Run test to verify it fails**

Run: `python manage.py test world.tests.test_pvp_state_cleanup.PvPStateCleanupTest -v 2`
Expected: FAIL

**Step 3: Write minimal implementation**

Clear local duel state on:
- leaving the arena room
- disconnect / unpuppet
- defeat resolution

Ensure the other participant is notified when appropriate.

**Step 4: Run test to verify it passes**

Run: `python manage.py test world.tests.test_pvp_state_cleanup.PvPStateCleanupTest -v 2`
Expected: PASS

**Step 5: Commit**

```bash
git add typeclasses/characters.py world/tests/test_pvp_state_cleanup.py
git commit -m "fix: clear arena duel state on exit and disconnect"
```

---

### Task 8: Add V3 PvP-specific persistence model

**Files:**
- Create: `world/pvp/apps.py`
- Create: `world/pvp/models.py`
- Create: `world/pvp/migrations/0001_initial.py`
- Modify: `server/conf/settings.py`
- Test: `world/pvp/tests/test_models.py`
- Reference: `world/achievements/models.py`

**Step 1: Write the failing model test**

```python
from django.test import TestCase


class PvPLogModelTest(TestCase):
    def test_log_stores_both_participants(self):
        self.fail("implement pvp log model test")
```

**Step 2: Run test to verify it fails**

Run: `python manage.py test world.pvp.tests.test_models.PvPLogModelTest -v 2`
Expected: FAIL

**Step 3: Write minimal implementation**

Create a separate app/model for PvP only. Include fields such as:
- challenger agent FK
- defender agent FK
- winner agent FK nullable
- result enum (`victory`, `defeat`, `yield`, `draw`, `flee`)
- room key
- started/ended timestamps

Do **not** modify the existing `CombatLog` model.

**Step 4: Create and review migration**

Run: `evennia makemigrations pvp`
Expected: migration file generated

**Step 5: Run test to verify it passes**

Run: `python manage.py test world.pvp.tests.test_models.PvPLogModelTest -v 2`
Expected: PASS

**Step 6: Commit**

```bash
git add world/pvp server/conf/settings.py
git commit -m "feat: add pvp log persistence app"
```

---

### Task 9: Add V3 arena points service

**Files:**
- Create: `world/pvp/services.py`
- Modify: `world/pvp/models.py`
- Test: `world/pvp/tests/test_points.py`

**Step 1: Write the failing tests**

```python
from django.test import TestCase


class ArenaPointsTest(TestCase):
    def test_daily_point_cap_blocks_extra_awards(self):
        self.fail("implement daily cap test")
```

**Step 2: Run test to verify it fails**

Run: `python manage.py test world.pvp.tests.test_points.ArenaPointsTest -v 2`
Expected: FAIL

**Step 3: Write minimal implementation**

Implement a service that:
- grants configured points for win/loss/draw
- tracks daily earned points
- refuses additional awards over the cap

Keep all numbers configurable in one place.

**Step 4: Run test to verify it passes**

Run: `python manage.py test world.pvp.tests.test_points.ArenaPointsTest -v 2`
Expected: PASS

**Step 5: Commit**

```bash
git add world/pvp/services.py world/pvp/tests/test_points.py
git commit -m "feat: add arena points service with daily cap"
```

---

### Task 10: Add V3 abuse controls and leaderboard-ready queries

**Files:**
- Modify: `world/pvp/services.py`
- Create: `world/pvp/query.py`
- Test: `world/pvp/tests/test_abuse_controls.py`

**Step 1: Write the failing tests**

```python
from django.test import TestCase


class AbuseControlsTest(TestCase):
    def test_repeat_pair_farming_is_reward_reduced(self):
        self.fail("implement repeat pair control test")
```

**Step 2: Run test to verify it fails**

Run: `python manage.py test world.pvp.tests.test_abuse_controls.AbuseControlsTest -v 2`
Expected: FAIL

**Step 3: Write minimal implementation**

Implement only the abuse rules supported by repository data:
- repeated pair reward reduction
- optional same-claim reward suppression if claim linkage is available
- level-gap reward suppression only if character level is a reliable signal

Explicitly defer IP-based controls unless a trusted IP storage source exists.

Add read queries for:
- top arena points
- recent duel history
- per-agent W/L/D totals

**Step 4: Run test to verify it passes**

Run: `python manage.py test world.pvp.tests.test_abuse_controls.AbuseControlsTest -v 2`
Expected: PASS

**Step 5: Commit**

```bash
git add world/pvp/services.py world/pvp/query.py world/pvp/tests/test_abuse_controls.py
git commit -m "feat: add arena abuse controls and ranking queries"
```

---

### Task 11: Full verification checkpoint after each phase

**Files:**
- Modify: docs only if needed
- Test: verification commands only

**Step 1: Verify V1**

Run:
```bash
python manage.py test world.tests.test_pvp_rooms world.tests.test_codeworld_definitions -v 2
evennia sync_codeworld
```
Expected: tests pass; world sync succeeds

**Step 2: Verify V2**

Run:
```bash
python manage.py test world.tests.test_pvp_commands world.tests.test_pvp_attack_gating world.tests.test_pvp_state_cleanup -v 2
```
Expected: PASS

**Step 3: Verify V3**

Run:
```bash
python manage.py test world.pvp -v 2
```
Expected: PASS

**Step 4: Run project smoke checks**

Run:
```bash
flake8 .
python manage.py test
```
Expected: project checks pass or only show unrelated pre-existing failures

**Step 5: Commit**

```bash
git add .
git commit -m "test: verify broken shore ring rollout"
```

---

## Design notes for implementers

- **Arena placement:** connect to a post-gatehouse or courtyard-adjacent non-PvP room, not Intro/Cliff/Bridge/Dark Cell.
- **Room semantics:** V1 intentionally allows direct PvP inside the arena. V2 is where consent becomes mandatory.
- **Modeling rule:** PvP persistence must remain separate from current PvE combat achievement storage.
- **Naming rule:** use `The Broken Shore Ring` in player-facing English copy; Chinese localization can be decided separately later.
- **Rollback safety:** V1 can be reverted by removing one room typeclass + one room/exit world definition, with no schema rollback.

## Recommended release strategy

1. Ship **V1** alone and observe agent behavior.
2. Only begin **V2** after confirming room placement and direct PvP do not create onboarding confusion.
3. Only begin **V3** after product decisions on points visibility, leaderboard scope, and anti-farming policy are approved.
