"""
Initial achievement data definitions.

This module defines the achievement data that can be loaded into the database.
"""

# Main quest achievements (10)
QUEST_ACHIEVEMENTS = [
    {
        'key': 'first_steps',
        'name': '初出茅庐',
        'description': '踏入 Tutorial World 的第一步',
        'category': 'exploration',
        'points': 10,
        'is_hidden': False,
        'requirement': {'room_key': 'tut#02'},
    },
    {
        'key': 'cliff_explorer',
        'name': '悬崖探险家',
        'description': '探索悬崖并攀爬树木',
        'category': 'exploration',
        'points': 15,
        'is_hidden': False,
        'requirement': {'room_key': 'tut#02', 'action': 'climb_tree'},
    },
    {
        'key': 'bridge_crosser',
        'name': '勇渡深渊',
        'description': '成功通过摇晃的桥梁',
        'category': 'exploration',
        'points': 20,
        'is_hidden': False,
        'requirement': {'room_key': 'tut#03'},
    },
    {
        'key': 'dark_survivor',
        'name': '黑暗幸存者',
        'description': '从黑暗区域成功逃脱',
        'category': 'exploration',
        'points': 25,
        'is_hidden': False,
        'requirement': {'room_key': 'tut#08'},  # Reached gatehouse from dark area
    },
    {
        'key': 'gatehouse_visitor',
        'name': '门房来客',
        'description': '到达古老的门房',
        'category': 'exploration',
        'points': 15,
        'is_hidden': False,
        'requirement': {'room_key': 'tut#08'},
    },
    {
        'key': 'temple_visitor',
        'name': '神庙访客',
        'description': '进入神秘的神庙',
        'category': 'exploration',
        'points': 15,
        'is_hidden': False,
        'requirement': {'room_key': 'tut#09'},
    },
    {
        'key': 'puzzle_solver',
        'name': '解谜大师',
        'description': '完成破碎之墙谜题',
        'category': 'puzzle',
        'points': 30,
        'is_hidden': False,
        'requirement': {'room_key': 'tut#12', 'puzzle': 'broken_wall'},
    },
    {
        'key': 'tomb_finder',
        'name': '墓穴发现者',
        'description': '找到正确的墓室',
        'category': 'exploration',
        'points': 25,
        'is_hidden': False,
        'requirement': {'room_key': 'tut#15'},
    },
    {
        'key': 'ghost_slayer',
        'name': '幽灵杀手',
        'description': '击败可怕的幽灵',
        'category': 'combat',
        'points': 30,
        'is_hidden': False,
        'requirement': {'type': 'kill_mob', 'mob_key': 'ghost', 'count': 1},
    },
    {
        'key': 'adventure_complete',
        'name': '冒险完成',
        'description': '完成整个 Tutorial World 冒险',
        'category': 'story',
        'points': 100,
        'is_hidden': False,
        'requirement': {'room_key': 'tut#16'},
    },
]

# Hidden achievements (3)
HIDDEN_ACHIEVEMENTS = [
    {
        'key': 'explorer_master',
        'name': '探索大师',
        'description': '访问全部 16 个房间',
        'category': 'exploration',
        'points': 50,
        'is_hidden': True,
        'requirement': {'type': 'visit_all_rooms', 'count': 16},
    },
    {
        'key': 'secret_finder',
        'name': '秘密发现者',
        'description': '发现隐藏的秘密区域',
        'category': 'exploration',
        'points': 30,
        'is_hidden': True,
        'requirement': {'type': 'find_secret'},
    },
    {
        'key': 'speedrunner',
        'name': '速度之星',
        'description': '在 5 分钟内完成游戏',
        'category': 'story',
        'points': 75,
        'is_hidden': True,
        'requirement': {'type': 'speedrun', 'minutes': 5},
    },
]

# Combat achievements (model ready, awaiting combat system)
COMBAT_ACHIEVEMENTS = [
    {
        'key': 'first_blood',
        'name': '初次胜利',
        'description': '击败第一个敌人',
        'category': 'combat',
        'points': 15,
        'is_hidden': False,
        'requirement': {'type': 'total_kills', 'count': 1},
    },
    {
        'key': 'monster_hunter',
        'name': '怪物猎人',
        'description': '击败 10 个敌人',
        'category': 'combat',
        'points': 50,
        'is_hidden': False,
        'requirement': {'type': 'total_kills', 'count': 10},
    },
    {
        'key': 'ghostbane',
        'name': '幽灵克星',
        'description': '击败幽灵 3 次',
        'category': 'combat',
        'points': 40,
        'is_hidden': False,
        'requirement': {'type': 'kill_mob', 'mob_key': 'ghost', 'count': 3},
    },
]

# All achievements combined
ALL_ACHIEVEMENTS = QUEST_ACHIEVEMENTS + HIDDEN_ACHIEVEMENTS + COMBAT_ACHIEVEMENTS


def load_initial_achievements():
    """
    Load initial achievement data into the database.

    This function should be called after migrations are applied.
    """
    from world.achievements.models import Achievement

    created_count = 0
    for data in ALL_ACHIEVEMENTS:
        _, created = Achievement.objects.get_or_create(
            key=data['key'],
            defaults=data
        )
        if created:
            created_count += 1

    return created_count