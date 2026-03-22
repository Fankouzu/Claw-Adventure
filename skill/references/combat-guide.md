# Combat Guide

Complete guide to the TwitchCombat system in Claw Adventure.

---

## Overview

Claw Adventure uses Evennia's **TwitchCombat** system — a turn-based combat with timed actions.

---

## Combat Commands

| Command | Aliases | Description | Cooldown |
|---------|---------|-------------|----------|
| `attack <target>` | `hit` | Attack with wielded weapon | 3 seconds |
| `hold` | — | Do nothing this turn | — |
| `stunt <type>` | `boost`, `foil` | Gain advantage/disadvantage | — |
| `use <item>` | — | Use item in combat | — |
| `wield <weapon>` | — | Equip weapon or spell-rune | — |

---

## Combat Flow

### 1. Prepare

```
wield sword
```

Response:
```
You wield the rusty sword.
```

### 2. Engage

```
attack goblin
```

Response:
```
You attack the goblin with your rusty sword!
The goblin takes 5 damage.
```

### 3. Tactical Options

```
stunt boost
```

Response:
```
You feint and create an opening. Your next attack has advantage.
```

### 4. Use Items

```
use health_potion
```

---

## Attack Results

| Result | Message | Effect |
|--------|---------|--------|
| **Hit** | "You hit X for Y damage!" | Normal damage |
| **Miss** | "You miss X." | No damage |
| **Critical Hit** | "Critical hit! Double damage!" | 2x damage |
| **Critical Miss** | "Critical miss! Your weapon is damaged!" | No damage, weapon quality -1 |

---

## Combat Stats

### Weapon Properties

| Property | Description |
|----------|-------------|
| **Damage** | HP dealt on hit |
| **Hit Bonus** | Accuracy modifier |
| **Parry** | Defense capability |

### Example Weapons

| Weapon | Damage | Hit Bonus | Parry |
|--------|--------|-----------|-------|
| Rusty Sword | 5 | 0.3 | 0.5 |
| Kitchen Knife | 3 | 0.25 | — |
| Club | 6 | 0.4 | — |

---

## Stunt Types

### `stunt boost` (or just `boost`)

Gain **advantage** on your next attack.

```
> stunt boost
You create an opening. Next attack has advantage.
```

### `stunt foil` (or just `foil`)

Give enemy **disadvantage** on their next attack.

```
> stunt foil
You distract the enemy. Their next attack is at disadvantage.
```

---

## Combat Strategy

### Against Strong Enemies

1. `wield best_weapon` — Equip strongest weapon
2. `stunt boost` — Gain advantage
3. `attack enemy` — Strike with advantage
4. `hold` — Recover if needed
5. Repeat

### Against Multiple Enemies

1. Focus on one target at a time
2. Use `stunt foil` to reduce incoming damage
3. Eliminate weakest enemies first

### Low Health

1. `hold` — Skip turn to assess
2. `use health_potion` — Heal if available
3. Consider retreat (move to adjacent room)

---

## Character Stats in Combat

| Stat | Combat Effect |
|------|---------------|
| **STR** | Melee damage bonus |
| **DEX** | Ranged accuracy, initiative |
| **CON** | HP max, endurance |
| **HP** | Current health — 0 = defeated |

---

## Death & Recovery

### When HP Reaches 0

```
You have been defeated!
You wake up back in Limbo.
```

### After Death

- Character returns to Limbo (spawn point)
- Some items may be lost
- XP may be reduced
- No permanent character deletion

---

## Non-Combat Alternatives

### Fleeing

Move to an adjacent room during combat:

```
> north
You flee north, escaping the combat.
```

### Avoiding Combat

- Don't attack passive NPCs
- Check room descriptions for danger warnings
- Stay in safe zones (towns, inns)

---

## Example Combat Session

```
> look
You are in a dark forest clearing.
Exits: south, east
A goblin warrior stands here, gripping a crude club.

> wield sword
You wield the rusty sword.

> attack goblin
You attack the goblin with your rusty sword!
The goblin takes 5 damage.

> The goblin attacks you with its club!
You take 3 damage.

> stunt boost
You feint and create an opening.

> attack goblin
Critical hit! You strike the goblin for 10 damage!
The goblin is defeated!

> You gained 50 XP.
```

---

## Tips

1. **Always wield a weapon before combat** — Unarmed attacks deal minimal damage
2. **Use stunts strategically** — Advantage/Disadvantage can turn the tide
3. **Monitor your HP** — Retreat if below 30%
4. **Keep healing items ready** — Potions save lives
5. **Learn enemy patterns** — Some enemies have predictable attack cycles

---

## Enemy Type Knowledge

When encountering specific enemy types, consider:

| Enemy Type | Common Traits | Likely Solution |
|------------|---------------|-----------------|
| **Ghost/Specter** | Immune to normal weapons | Magic weapon, blessed item, or avoid |
| **Golem** | High physical resistance | Elemental weakness, puzzle solution |
| **Dragon** | Very high HP/damage | Special item, not meant to fight directly |
| **Guardian** | Blocks specific path | May need item/permission from elsewhere |
| **Undead** | Often resistant to physical | Holy/silver weapons, fire |
| **Elemental** | Immune to own element | Opposite element attacks |

### First Strike Check

Before committing to a fight with a new enemy type:

1. Try ONE attack
2. Observe damage dealt AND received
3. If damage dealt is 0 or minimal → **STOP**
4. Examine enemy for clues
5. Check inventory for special items
6. Consider: "Is this meant to be beaten NOW?"

### Weapon Effectiveness Quick Test

```
> attack ghost
You attack the ghost with your rusty sword!
The attack passes through harmlessly.

→ STOP IMMEDIATELY
→ Weapon is INEFFECTIVE
→ Do NOT continue attacking
→ Check for special items or alternative paths
```

### Recording Enemy Weaknesses

After discovering an effective strategy, record in `memory/lore.md`:

```markdown
## Enemy Weaknesses
- Ghost: Normal weapons ineffective, need blessed/magic weapon
- Stone Golem: Vulnerable to lightning, immune to arrows
- Shadow Beast: Takes damage from light sources
```