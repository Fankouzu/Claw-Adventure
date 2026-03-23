# The Broken Shore Ring PvP Progression Design

**Feature:** Add an arena-only PvP progression system for **The Broken Shore Ring**.

## Goals

- Reward actual PvP participation inside the arena without touching main character XP or level.
- Make rewards proportional to real contribution by using damage dealt rather than only the final blow.
- Allow all players to inspect their own and others' PvP progression.
- Prevent simple farming loops from turning the ring into an abusable progression source.

## Scope Boundary

- Applies only inside `Claw / The Broken Shore Ring`.
- Applies only to player-vs-player combat.
- Does not apply to `The Salt-Worn Sparring Effigy`.
- Does not apply to ghosts, mobs, or other PvE combat.
- Does not change `Character.xp`, `Character.level`, or other main-game progression.

## Data Model

Store independent PvP progression on the Character object.

- `pvp_rank` (default 1)
- `pvp_xp` (default 0)
- `pvp_xp_per_rank` (default 100)
- `pvp_damage_dealt_lifetime` (default 0)
- `pvp_wins` (default 0)
- `pvp_losses` (default 0)
- `pvp_opponent_reward_counts` (mapping of opponent id -> rewarded match count)

## Reward Rule

### Base reward

- `BASE_XP = 40`

### Damage-based allocation

At the end of a valid arena PvP fight:

```text
xp = round(BASE_XP * personal_damage / total_damage)
```

If no effective damage was dealt by either participant, no PvP XP is awarded.

### Rank progression

- `next_rank_xp = pvp_rank * pvp_xp_per_rank`
- `pvp_xp_per_rank = 100`
- PvP rank is display-only for V1 of this system; it does not grant combat stats.

## Match Resolution

A valid arena PvP result must satisfy all of the following:

- Both participants are real player characters.
- Both were in `BrokenShoreRingRoom`.
- At least one side dealt effective damage.
- The fight ends with one player defeating the other.

The winner receives a win count increment; the defeated player receives a loss count increment.
Both sides may still receive PvP XP if they contributed damage.

## Anti-Farming Rules

### Repeated-opponent decay

For repeated rewarded fights against the same opponent:

- 1st rewarded fight: 100%
- 2nd rewarded fight: 50%
- 3rd rewarded fight: 25%
- 4th and later: 0%

This decay applies independently to both participants' rewards.

### No-damage rule

- If total effective damage is 0, award 0 PvP XP.

## Commands

Add a single player-facing status command with aliases:

- `progress`
- `rank`
- `pvp`

### Usage

- `progress` → show your own PvP progression
- `progress <name>` → show another character's PvP progression

### Output fields

- PvP Rank
- PvP XP
- XP to next rank
- Wins
- Losses
- Lifetime PvP damage dealt

## English-only in-game copy

### XP gain
- `You gain {xp} PvP XP.`

### Rank up
- `Your PvP rank rises to Rank {rank}.`

### No reward
- `No PvP XP is awarded for this fight.`

### Progress header
- `PvP Progress`

## Non-Goals

- PvP stat bonuses from rank
- Global PvP outside the arena
- Elo / matchmaking
- IP / claim-based anti-cheat
- Seasonal ranking

## Deployment Safety

- Data lives on character attributes, so no schema migration is required for the first version.
- The system can be rolled back by removing the reward hooks and command registration without affecting main progression.
