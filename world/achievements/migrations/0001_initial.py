# Generated manually for achievements app

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('agent_auth', '__first__'),
    ]

    operations = [
        migrations.CreateModel(
            name='Achievement',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, help_text='Unique identifier', primary_key=True, serialize=False)),
                ('key', models.CharField(help_text="Unique key, e.g. 'first_steps'", max_length=100, unique=True)),
                ('name', models.CharField(help_text='Display name', max_length=200)),
                ('description', models.TextField(help_text='Achievement description')),
                ('category', models.CharField(choices=[('exploration', 'Exploration'), ('puzzle', 'Puzzle'), ('story', 'Story'), ('combat', 'Combat')], help_text='Achievement category', max_length=20)),
                ('points', models.IntegerField(default=10, help_text='Achievement points')),
                ('is_hidden', models.BooleanField(default=False, help_text='Hidden achievements are not shown until unlocked')),
                ('icon', models.CharField(blank=True, help_text='Icon identifier for UI', max_length=100)),
                ('requirement', models.JSONField(default=dict, help_text='JSON configuration for unlock condition')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': 'Achievement',
                'verbose_name_plural': 'Achievements',
                'db_table': 'achievements',
                'ordering': ['category', 'points'],
            },
        ),
        migrations.CreateModel(
            name='CombatLog',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('enemy_key', models.CharField(help_text='Enemy identifier', max_length=100)),
                ('enemy_name', models.CharField(help_text='Enemy display name', max_length=200)),
                ('result', models.CharField(choices=[('victory', 'Victory'), ('defeat', 'Defeat'), ('flee', 'Flee')], help_text='Combat result', max_length=20)),
                ('damage_dealt', models.IntegerField(default=0, help_text='Damage dealt to enemy')),
                ('damage_taken', models.IntegerField(default=0, help_text='Damage taken from enemy')),
                ('combat_time', models.DateTimeField(auto_now_add=True)),
                ('agent', models.ForeignKey(help_text='The participating agent', on_delete=models.deletion.CASCADE, related_name='combat_logs', to='agent_auth.agent')),
            ],
            options={
                'verbose_name': 'Combat Log',
                'verbose_name_plural': 'Combat Logs',
                'db_table': 'combat_logs',
                'ordering': ['-combat_time'],
            },
        ),
        migrations.CreateModel(
            name='ExplorationProgress',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('room_key', models.CharField(help_text="Room identifier, e.g. 'tut#05'", max_length=100)),
                ('room_name', models.CharField(help_text='Room name for display', max_length=200)),
                ('visited_at', models.DateTimeField(auto_now_add=True)),
                ('agent', models.ForeignKey(help_text='The exploring agent', on_delete=models.deletion.CASCADE, related_name='exploration_progress', to='agent_auth.agent')),
            ],
            options={
                'verbose_name': 'Exploration Progress',
                'verbose_name_plural': 'Exploration Progress',
                'db_table': 'exploration_progress',
                'ordering': ['agent', 'visited_at'],
            },
        ),
        migrations.CreateModel(
            name='UserAchievement',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('unlocked_at', models.DateTimeField(auto_now_add=True)),
                ('achievement', models.ForeignKey(help_text='The unlocked achievement', on_delete=models.deletion.CASCADE, related_name='unlockers', to='achievements.achievement')),
                ('agent', models.ForeignKey(help_text='The agent who unlocked this achievement', on_delete=models.deletion.CASCADE, related_name='unlocked_achievements', to='agent_auth.agent')),
            ],
            options={
                'verbose_name': 'User Achievement',
                'verbose_name_plural': 'User Achievements',
                'db_table': 'user_achievements',
                'ordering': ['-unlocked_at'],
            },
        ),
        migrations.AlterUniqueTogether(
            name='explorationprogress',
            unique_together={('agent', 'room_key')},
        ),
        migrations.AlterUniqueTogether(
            name='userachievement',
            unique_together={('agent', 'achievement')},
        ),
    ]