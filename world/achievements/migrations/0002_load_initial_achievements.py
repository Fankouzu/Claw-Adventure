# Data migration to load initial achievements

from django.db import migrations


def load_achievements(apps, schema_editor):
    """
    Load initial achievement data into the database.
    """
    Achievement = apps.get_model('achievements', 'Achievement')

    # Main quest achievements (10)
    quest_achievements = [
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
            'requirement': {'room_key': 'tut#08'},
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
    hidden_achievements = [
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
    combat_achievements = [
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

    all_achievements = quest_achievements + hidden_achievements + combat_achievements

    for data in all_achievements:
        Achievement.objects.get_or_create(
            key=data['key'],
            defaults=data
        )


class Migration(migrations.Migration):

    dependencies = [
        ('achievements', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(load_achievements),
    ]