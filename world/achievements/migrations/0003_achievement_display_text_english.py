# English display strings for achievements (player-facing copy).

from django.db import migrations


# key -> (name, description)
_ENGLISH = {
    "first_steps": (
        "First Steps",
        "Take your first step into the Tutorial World.",
    ),
    "cliff_explorer": (
        "Cliff Explorer",
        "Explore the cliff and climb the tree.",
    ),
    "bridge_crosser": (
        "Bridge Crosser",
        "Cross the swaying bridge safely.",
    ),
    "dark_survivor": (
        "Dark Survivor",
        "Escape from the dark depths.",
    ),
    "gatehouse_visitor": (
        "Gatehouse Visitor",
        "Reach the old gatehouse.",
    ),
    "temple_visitor": (
        "Temple Visitor",
        "Enter the mysterious temple.",
    ),
    "puzzle_solver": (
        "Puzzle Solver",
        "Solve the crumbling wall puzzle.",
    ),
    "tomb_finder": (
        "Tomb Finder",
        "Find the correct tomb.",
    ),
    "ghost_slayer": (
        "Ghost Slayer",
        "Defeat the fearsome ghost.",
    ),
    "adventure_complete": (
        "Adventure Complete",
        "Finish the entire Tutorial World.",
    ),
    "explorer_master": (
        "Master Explorer",
        "Visit all 16 rooms.",
    ),
    "secret_finder": (
        "Secret Finder",
        "Discover a hidden area.",
    ),
    "speedrunner": (
        "Speedrunner",
        "Finish the game within 5 minutes.",
    ),
    "first_blood": (
        "First Blood",
        "Defeat your first enemy.",
    ),
    "monster_hunter": (
        "Monster Hunter",
        "Defeat 10 enemies.",
    ),
    "ghostbane": (
        "Ghostbane",
        "Defeat the ghost 3 times.",
    ),
}


def forwards(apps, schema_editor):
    Achievement = apps.get_model("achievements", "Achievement")
    for key, (name, desc) in _ENGLISH.items():
        Achievement.objects.filter(key=key).update(name=name, description=desc)


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("achievements", "0002_load_initial_achievements"),
    ]

    operations = [
        migrations.RunPython(forwards, noop_reverse),
    ]
