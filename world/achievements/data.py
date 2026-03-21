"""
Initial achievement data definitions.

This module defines the achievement data that can be loaded into the database.
"""

# Main quest achievements (10)
QUEST_ACHIEVEMENTS = [
    {
        'key': 'first_steps',
        'name': 'First Steps',
        'description': 'Take your first step into the Tutorial World.',
        'category': 'exploration',
        'points': 10,
        'is_hidden': False,
        'requirement': {'room_key': 'tut#02'},
    },
    {
        'key': 'cliff_explorer',
        'name': 'Cliff Explorer',
        'description': 'Explore the cliff and climb the tree.',
        'category': 'exploration',
        'points': 15,
        'is_hidden': False,
        'requirement': {'room_key': 'tut#02', 'action': 'climb_tree'},
    },
    {
        'key': 'bridge_crosser',
        'name': 'Bridge Crosser',
        'description': 'Cross the swaying bridge safely.',
        'category': 'exploration',
        'points': 20,
        'is_hidden': False,
        'requirement': {'room_key': 'tut#03'},
    },
    {
        'key': 'dark_survivor',
        'name': 'Dark Survivor',
        'description': 'Escape from the dark depths.',
        'category': 'exploration',
        'points': 25,
        'is_hidden': False,
        'requirement': {'room_key': 'tut#08'},  # Reached gatehouse from dark area
    },
    {
        'key': 'gatehouse_visitor',
        'name': 'Gatehouse Visitor',
        'description': 'Reach the old gatehouse.',
        'category': 'exploration',
        'points': 15,
        'is_hidden': False,
        'requirement': {'room_key': 'tut#08'},
    },
    {
        'key': 'temple_visitor',
        'name': 'Temple Visitor',
        'description': 'Enter the mysterious temple.',
        'category': 'exploration',
        'points': 15,
        'is_hidden': False,
        'requirement': {'room_key': 'tut#09'},
    },
    {
        'key': 'puzzle_solver',
        'name': 'Puzzle Solver',
        'description': 'Solve the crumbling wall puzzle.',
        'category': 'puzzle',
        'points': 30,
        'is_hidden': False,
        'requirement': {'room_key': 'tut#12', 'puzzle': 'broken_wall'},
    },
    {
        'key': 'tomb_finder',
        'name': 'Tomb Finder',
        'description': 'Find the correct tomb.',
        'category': 'exploration',
        'points': 25,
        'is_hidden': False,
        'requirement': {'room_key': 'tut#15'},
    },
    {
        'key': 'ghost_slayer',
        'name': 'Ghost Slayer',
        'description': 'Defeat the fearsome ghost.',
        'category': 'combat',
        'points': 30,
        'is_hidden': False,
        'requirement': {'type': 'kill_mob', 'mob_key': 'ghost', 'count': 1},
    },
    {
        'key': 'adventure_complete',
        'name': 'Adventure Complete',
        'description': 'Finish the entire Tutorial World.',
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
        'name': 'Master Explorer',
        'description': 'Visit all 16 rooms.',
        'category': 'exploration',
        'points': 50,
        'is_hidden': True,
        'requirement': {'type': 'visit_all_rooms', 'count': 16},
    },
    {
        'key': 'secret_finder',
        'name': 'Secret Finder',
        'description': 'Discover a hidden area.',
        'category': 'exploration',
        'points': 30,
        'is_hidden': True,
        'requirement': {'type': 'find_secret'},
    },
    {
        'key': 'speedrunner',
        'name': 'Speedrunner',
        'description': 'Finish the game within 5 minutes.',
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
        'name': 'First Blood',
        'description': 'Defeat your first enemy.',
        'category': 'combat',
        'points': 15,
        'is_hidden': False,
        'requirement': {'type': 'total_kills', 'count': 1},
    },
    {
        'key': 'monster_hunter',
        'name': 'Monster Hunter',
        'description': 'Defeat 10 enemies.',
        'category': 'combat',
        'points': 50,
        'is_hidden': False,
        'requirement': {'type': 'total_kills', 'count': 10},
    },
    {
        'key': 'ghostbane',
        'name': 'Ghostbane',
        'description': 'Defeat the ghost 3 times.',
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
