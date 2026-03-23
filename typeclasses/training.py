from django.utils import timezone


TRAINING_EFFIGY_DAILY_CAP = 250
TRAINING_EFFIGY_LIFETIME_CAP = 1500
TRAINING_EFFIGY_XP_BY_LEVEL = {
    1: 25,
    2: 18,
    3: 12,
    4: 8,
    5: 4,
}


def _today_key() -> str:
    return timezone.now().date().isoformat()


def _reset_daily_xp_if_needed(character) -> None:
    today = _today_key()
    if getattr(character.db, "training_effigy_last_reset", "") == today:
        return
    character.db.training_effigy_last_reset = today
    character.db.training_effigy_daily_xp = 0


def _apply_level_ups(character) -> None:
    if not hasattr(character, "max_hp"):
        character.max_hp = character.hp_max
    while character.xp >= character.level * character.xp_per_level:
        character.level_up()


def grant_training_effigy_xp(character) -> int:
    if not character or not getattr(character, "is_pc", False):
        return 0

    _reset_daily_xp_if_needed(character)

    base_xp = TRAINING_EFFIGY_XP_BY_LEVEL.get(int(character.level), 0)
    if base_xp <= 0:
        character.msg("Your skills have outgrown what this effigy can teach.")
        return 0

    daily_xp = int(getattr(character.db, "training_effigy_daily_xp", 0) or 0)
    lifetime_xp = int(getattr(character.db, "training_effigy_lifetime_xp", 0) or 0)

    remaining_daily = max(0, TRAINING_EFFIGY_DAILY_CAP - daily_xp)
    remaining_lifetime = max(0, TRAINING_EFFIGY_LIFETIME_CAP - lifetime_xp)
    award = min(base_xp, remaining_daily, remaining_lifetime)

    if award <= 0:
        if remaining_lifetime <= 0:
            character.msg("The effigy has nothing more to teach you.")
        else:
            character.msg("You cannot learn any more from the effigy today.")
        return 0

    character.db.training_effigy_daily_xp = daily_xp + award
    character.db.training_effigy_lifetime_xp = lifetime_xp + award
    character.add_xp(award)
    _apply_level_ups(character)
    character.msg("You learn a little from striking the Salt-Worn Sparring Effigy.")
    return award
