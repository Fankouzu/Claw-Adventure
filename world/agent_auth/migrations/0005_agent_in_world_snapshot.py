# Generated manually for Agent in-world mirror columns

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("agent_auth", "0004_invitationcode_code_type_invitationcode_created_by_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="agent",
            name="in_world_character_key",
            field=models.CharField(
                blank=True,
                default="",
                help_text="EvAdventure character key at last sync",
                max_length=255,
            ),
        ),
        migrations.AddField(
            model_name="agent",
            name="in_world_hp",
            field=models.IntegerField(default=0, help_text="Mirrored Character.hp"),
        ),
        migrations.AddField(
            model_name="agent",
            name="in_world_hp_max",
            field=models.IntegerField(default=0, help_text="Mirrored Character.hp_max"),
        ),
        migrations.AddField(
            model_name="agent",
            name="in_world_level",
            field=models.IntegerField(default=1, help_text="Mirrored Character.level"),
        ),
        migrations.AddField(
            model_name="agent",
            name="in_world_xp",
            field=models.IntegerField(default=0, help_text="Mirrored Character.xp"),
        ),
        migrations.AddField(
            model_name="agent",
            name="in_world_xp_per_level",
            field=models.IntegerField(
                default=1000,
                help_text="Mirrored Character.xp_per_level (EvAdventure default 1000)",
            ),
        ),
        migrations.AddField(
            model_name="agent",
            name="in_world_coins",
            field=models.IntegerField(default=0, help_text="Mirrored Character.coins"),
        ),
        migrations.AddField(
            model_name="agent",
            name="in_world_strength",
            field=models.IntegerField(default=1, help_text="Mirrored STR bonus"),
        ),
        migrations.AddField(
            model_name="agent",
            name="in_world_dexterity",
            field=models.IntegerField(default=1, help_text="Mirrored DEX bonus"),
        ),
        migrations.AddField(
            model_name="agent",
            name="in_world_constitution",
            field=models.IntegerField(default=1, help_text="Mirrored CON bonus"),
        ),
        migrations.AddField(
            model_name="agent",
            name="in_world_intelligence",
            field=models.IntegerField(default=1, help_text="Mirrored INT bonus"),
        ),
        migrations.AddField(
            model_name="agent",
            name="in_world_wisdom",
            field=models.IntegerField(default=1, help_text="Mirrored WIS bonus"),
        ),
        migrations.AddField(
            model_name="agent",
            name="in_world_charisma",
            field=models.IntegerField(default=1, help_text="Mirrored CHA bonus"),
        ),
        migrations.AddField(
            model_name="agent",
            name="in_world_synced_at",
            field=models.DateTimeField(
                blank=True,
                help_text="When in-world fields were last copied from the Character",
                null=True,
            ),
        ),
    ]
