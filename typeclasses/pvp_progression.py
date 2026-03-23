PVP_BASE_XP = 40
PVP_XP_PER_RANK = 100
PVP_REPEAT_DECAY = (1.0, 0.5, 0.25, 0.0)


def is_arena_pvp(attacker, defender) -> bool:
    from typeclasses.pvp_rooms import BrokenShoreRingRoom

    room = getattr(defender, "location", None)
    return bool(
        room
        and isinstance(room, BrokenShoreRingRoom)
        and attacker is not defender
        and getattr(attacker, "is_pc", False)
        and getattr(defender, "is_pc", False)
    )


def _damage_key(opponent) -> str:
    return str(opponent.id)


def _get_damage_map(character) -> dict:
    damage_map = getattr(character.ndb, "pvp_ring_damage", None)
    if damage_map is None:
        damage_map = {}
        character.ndb.pvp_ring_damage = damage_map
    return damage_map


def record_arena_pvp_damage(attacker, defender, damage: int) -> None:
    if damage <= 0 or not is_arena_pvp(attacker, defender):
        return
    damage_map = _get_damage_map(attacker)
    key = _damage_key(defender)
    damage_map[key] = int(damage_map.get(key, 0) or 0) + int(damage)


def _get_stat(character, key: str, default: int) -> int:
    return int(getattr(character.db, key, default) or default)


def _set_stat(character, key: str, value: int) -> None:
    setattr(character.db, key, int(value))


def _repeat_multiplier(character, opponent) -> float:
    counts = getattr(character.db, "pvp_opponent_reward_counts", None) or {}
    count = int(counts.get(_damage_key(opponent), 0) or 0)
    idx = min(count, len(PVP_REPEAT_DECAY) - 1)
    return PVP_REPEAT_DECAY[idx]


def _increment_repeat_count(character, opponent) -> None:
    counts = dict(getattr(character.db, "pvp_opponent_reward_counts", None) or {})
    key = _damage_key(opponent)
    counts[key] = int(counts.get(key, 0) or 0) + 1
    character.db.pvp_opponent_reward_counts = counts


def _apply_pvp_rank_ups(character) -> list[int]:
    rank = _get_stat(character, "pvp_rank", 1)
    xp = _get_stat(character, "pvp_xp", 0)
    ranks = []
    while xp >= rank * PVP_XP_PER_RANK:
        rank += 1
        ranks.append(rank)
    _set_stat(character, "pvp_rank", rank)
    return ranks


def _award_pvp_xp(character, opponent, damage, total_damage) -> int:
    if total_damage <= 0 or damage <= 0:
        return 0
    raw_award = round(PVP_BASE_XP * damage / total_damage)
    award = round(raw_award * _repeat_multiplier(character, opponent))
    _set_stat(character, "pvp_xp", _get_stat(character, "pvp_xp", 0) + award)
    _set_stat(
        character,
        "pvp_damage_dealt_lifetime",
        _get_stat(character, "pvp_damage_dealt_lifetime", 0) + damage,
    )
    _increment_repeat_count(character, opponent)
    if award > 0:
        character.msg(f"You gain {award} PvP XP.")
        for rank in _apply_pvp_rank_ups(character):
            character.msg(f"Your PvP rank rises to Rank {rank}.")
    else:
        character.msg("No PvP XP is awarded for this fight.")
    return award


def resolve_arena_pvp_defeat(winner, loser) -> None:
    winner_damage = int(_get_damage_map(winner).get(_damage_key(loser), 0) or 0)
    loser_damage = int(_get_damage_map(loser).get(_damage_key(winner), 0) or 0)
    total_damage = winner_damage + loser_damage

    _set_stat(winner, "pvp_wins", _get_stat(winner, "pvp_wins", 0) + 1)
    _set_stat(loser, "pvp_losses", _get_stat(loser, "pvp_losses", 0) + 1)

    _award_pvp_xp(winner, loser, winner_damage, total_damage)
    _award_pvp_xp(loser, winner, loser_damage, total_damage)

    _get_damage_map(winner).pop(_damage_key(loser), None)
    _get_damage_map(loser).pop(_damage_key(winner), None)


def build_pvp_progress_lines(character, title: str) -> str:
    rank = _get_stat(character, "pvp_rank", 1)
    xp = _get_stat(character, "pvp_xp", 0)
    next_rank_xp = max(0, rank * PVP_XP_PER_RANK - xp)
    wins = _get_stat(character, "pvp_wins", 0)
    losses = _get_stat(character, "pvp_losses", 0)
    lifetime_damage = _get_stat(character, "pvp_damage_dealt_lifetime", 0)
    return (
        f"{title}\n"
        f"Rank: {rank}\n"
        f"XP: {xp}\n"
        f"XP to next rank: {next_rank_xp}\n"
        f"Wins: {wins}\n"
        f"Losses: {losses}\n"
        f"Lifetime PvP damage dealt: {lifetime_damage}"
    )
