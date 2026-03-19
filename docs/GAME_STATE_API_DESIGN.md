# 游戏状态API设计规范

## 概述

本文档定义了如何为 Evennia MUD 游戏创建外部 API，使 AI Agent 能够获取游戏状态数据。

---

## 一、Evennia 内置 REST API

Evennia **已内置完整的 Django REST Framework API**，无需从头开发。

### 启用方式

在 `server/conf/settings.py` 中添加：

```python
# 启用 REST API
REST_API_ENABLED = True

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'evennia.web.api.permissions.EvenniaPermission',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 50,
}
```

### 内置 API 端点

| 端点 | 方法 | 描述 |
|------|------|------|
| `/api/accounts/` | GET/POST | 账户列表/创建 |
| `/api/accounts/<pk>/` | GET/PUT/DELETE | 账户详情 |
| `/api/objects/` | GET/POST | 对象列表/创建 |
| `/api/objects/<pk>/` | GET/PUT/DELETE | 对象详情 |
| `/api/characters/` | GET/POST | 角色列表 |
| `/api/rooms/` | GET/POST | 房间列表 |
| `/api/exits/` | GET/POST | 出口列表 |
| `/api/scripts/` | GET/POST | 脚本列表 |
| `/api/objects/<pk>/set-attribute/` | PUT | 设置属性 |
| `/api/openapi` | GET | OpenAPI Schema |
| `/api/redoc/` | GET | API 文档 |

### 查询过滤器

```
# 按名称搜索
GET /api/objects/?db_key=PlayerName

# 按标签搜索
GET /api/objects/?db_tags__db_key=goblin&db_tags__db_category=monster

# 按位置搜索
GET /api/objects/?db_location__id=5

# 按类型搜索
GET /api/objects/?db_typeclass_path__contains=Character
```

---

## 二、游戏状态数据模型

### 2.1 Agent 位置状态

**数据来源：**
```python
from evennia.objects.models import ObjectDB

# 获取角色
character = ObjectDB.objects.get(db_key="CharacterName")

# 当前位置
location = character.db_location
location_name = location.db_key
location_id = location.id
location_typeclass = location.db_typeclass_path
```

**API 响应示例：**
```json
{
    "character_id": 42,
    "character_name": "Agent_Alpha",
    "location": {
        "id": 5,
        "name": "Temple",
        "typeclass": "typeclasses.rooms.TutorialRoom",
        "coordinates": {"x": null, "y": null},
        "zone": "castle"
    },
    "previous_location": {
        "id": 4,
        "name": "Gatehouse"
    },
    "entered_at": "2024-03-18T10:30:00Z"
}
```

### 2.2 Agent 探索记录

**实现方式：使用 Tag 系统追踪已访问房间**

```python
# 访问房间时添加标签
character.tags.add("tut#05", category="visited_rooms")

# 查询已访问房间
visited = character.tags.get(category="visited_rooms")
# 返回: ["tut#01", "tut#02", "tut#03", ...]

# 检查是否访问过特定房间
has_visited = character.tags.has("tut#05", category="visited_rooms")
```

**API 响应示例：**
```json
{
    "agent_id": "agent_123",
    "total_rooms": 16,
    "visited_rooms": [
        {"room_id": 1, "name": "Intro Room", "visited_at": "2024-03-18T10:00:00Z"},
        {"room_id": 2, "name": "Cliff", "visited_at": "2024-03-18T10:05:00Z"},
        {"room_id": 3, "name": "Bridge", "visited_at": "2024-03-18T10:10:00Z"}
    ],
    "exploration_percentage": 18.75,
    "last_visited": {
        "room_id": 3,
        "name": "Bridge",
        "visited_at": "2024-03-18T10:10:00Z"
    }
}
```

### 2.3 Agent 物品清单

**数据来源：**
```python
# 获取角色携带的所有物品
inventory = character.contents  # 返回 ObjectDB 列表

# 过滤非出口物品
items = [obj for obj in inventory if not obj.destination]

# 物品详情
for item in items:
    print(f"Name: {item.db_key}")
    print(f"Type: {item.db_typeclass_path}")
    print(f"Attributes: {item.attributes.all()}")
```

**API 响应示例：**
```json
{
    "agent_id": "agent_123",
    "inventory": [
        {
            "id": 100,
            "name": "Rusty Sword",
            "type": "weapon",
            "typeclass": "evennia.contrib.tutorials.tutorial_world.objects.TutorialWeapon",
            "attributes": {
                "damage": 10,
                "damage_type": "slash"
            },
            "equipped": true
        },
        {
            "id": 101,
            "name": "Torch",
            "type": "light_source",
            "typeclass": "evennia.contrib.tutorials.tutorial_world.objects.LightSource",
            "attributes": {
                "burn_time_remaining": 120
            },
            "equipped": false
        }
    ],
    "capacity": {
        "current": 2,
        "max": 10
    },
    "weight": {
        "current": 15,
        "max": 100
    }
}
```

### 2.4 Agent 属性系统

**数据来源：**
```python
# 获取所有属性
all_attrs = character.attributes.all()

# 获取特定属性
health = character.db.health
max_health = character.db.max_health
mana = character.db.mana
experience = character.db.experience
level = character.db.level

# 或按类别获取
combat_attrs = character.attributes.get(category="combat")
```

**API 响应示例：**
```json
{
    "agent_id": "agent_123",
    "attributes": {
        "core": {
            "health": 80,
            "max_health": 100,
            "mana": 50,
            "max_mana": 100,
            "stamina": 90,
            "max_stamina": 100
        },
        "progression": {
            "level": 5,
            "experience": 1250,
            "experience_to_next_level": 2000
        },
        "combat": {
            "attack": 15,
            "defense": 10,
            "critical_chance": 5
        },
        "skills": {
            "stealth": 3,
            "perception": 5,
            "lockpicking": 2
        }
    },
    "derived_stats": {
        "damage_reduction": "10%",
        "health_regen": "2 HP/min",
        "mana_regen": "5 MP/min"
    }
}
```

### 2.5 Agent 经验与等级

**数据来源（项目已有模型）：**
```python
# 来自 world.agent_auth.models.Agent
from world.agent_auth.models import Agent

agent = Agent.objects.get(id=agent_id)
level = agent.level
experience = agent.experience
```

**API 响应示例：**
```json
{
    "agent_id": "agent_123",
    "level": 5,
    "experience": {
        "current": 1250,
        "total_for_current_level": 1000,
        "required_for_next_level": 2000,
        "progress_percentage": 25.0
    },
    "level_up_available": false,
    "unspent_skill_points": 0,
    "level_history": [
        {"level": 1, "achieved_at": "2024-03-01T00:00:00Z"},
        {"level": 2, "achieved_at": "2024-03-05T00:00:00Z"},
        {"level": 3, "achieved_at": "2024-03-10T00:00:00Z"},
        {"level": 4, "achieved_at": "2024-03-15T00:00:00Z"},
        {"level": 5, "achieved_at": "2024-03-18T00:00:00Z"}
    ]
}
```

---

## 三、成就系统设计

### 3.1 数据模型

```python
# world/achievements/models.py
from django.db import models
from world.agent_auth.models import Agent

class Achievement(models.Model):
    """成就定义"""
    ACHIEVEMENT_TYPES = [
        ('exploration', '探索成就'),
        ('combat', '战斗成就'),
        ('puzzle', '解谜成就'),
        ('hidden', '隐藏成就'),
        ('story', '剧情成就'),
    ]

    key = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=200)
    description = models.TextField()
    achievement_type = models.CharField(max_length=20, choices=ACHIEVEMENT_TYPES)
    icon = models.CharField(max_length=50, blank=True)
    is_hidden = models.BooleanField(default=False)
    points = models.IntegerField(default=10)
    requirements = models.JSONField(default=dict)  # 解锁条件

    class Meta:
        db_table = 'achievements'


class AgentAchievement(models.Model):
    """Agent获得的成就"""
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE, related_name='achievements')
    achievement = models.ForeignKey(Achievement, on_delete=models.CASCADE)
    unlocked_at = models.DateTimeField(auto_now_add=True)
    progress = models.IntegerField(default=100)  # 进度百分比

    class Meta:
        db_table = 'agent_achievements'
        unique_together = ['agent', 'achievement']
```

### 3.2 成就定义

```python
# world/achievements/data.py

ACHIEVEMENTS = [
    # 探索成就
    {
        "key": "first_steps",
        "name": "初出茅庐",
        "description": "离开 Intro Room 进入游戏世界",
        "type": "exploration",
        "points": 5,
        "requirements": {"visited_rooms": ["tut#02"]}
    },
    {
        "key": "explorer_novice",
        "name": "探索新手",
        "description": "访问 5 个不同的房间",
        "type": "exploration",
        "points": 10,
        "requirements": {"visited_rooms_count": 5}
    },
    {
        "key": "explorer_master",
        "name": "探索大师",
        "description": "访问所有 16 个房间",
        "type": "exploration",
        "points": 50,
        "requirements": {"visited_rooms_count": 16}
    },
    {
        "key": "hidden_area",
        "name": "秘密发现者",
        "description": "找到隐藏区域",
        "type": "hidden",
        "is_hidden": True,
        "points": 25,
        "requirements": {"visited_rooms": ["hidden_area"]}
    },

    # 战斗成就
    {
        "key": "first_blood",
        "name": "初次胜利",
        "description": "击败第一个敌人",
        "type": "combat",
        "points": 15,
        "requirements": {"kills": 1}
    },
    {
        "key": "ghost_slayer",
        "name": "幽灵杀手",
        "description": "击败 Gatehouse 的幽灵",
        "type": "combat",
        "points": 25,
        "requirements": {"killed_mobs": ["ghostly_apparition"]}
    },

    # 解谜成就
    {
        "key": "puzzle_solver",
        "name": "解谜高手",
        "description": "解开 Crumbling Wall 谜题",
        "type": "puzzle",
        "points": 30,
        "requirements": {"puzzles_solved": ["crumbling_wall"]}
    },
    {
        "key": "dark_escape",
        "name": "黑暗逃脱",
        "description": "在光源燃尽前逃离黑暗区域",
        "type": "puzzle",
        "points": 20,
        "requirements": {"events": ["dark_escape"]}
    },

    # 剧情成就
    {
        "key": "game_complete",
        "name": "冒险完成",
        "description": "到达 Ancient Tomb 完成游戏",
        "type": "story",
        "points": 100,
        "requirements": {"visited_rooms": ["tut#16"]}
    },

    # 隐藏成就
    {
        "key": "speedrunner",
        "name": "速度之星",
        "description": "在 5 分钟内完成游戏",
        "type": "hidden",
        "is_hidden": True,
        "points": 75,
        "requirements": {"completion_time_seconds": 300}
    },
    {
        "key": "pacifist",
        "name": "和平主义者",
        "description": "不击杀任何敌人完成游戏",
        "type": "hidden",
        "is_hidden": True,
        "points": 100,
        "requirements": {"kills": 0, "game_completed": True}
    },
    {
        "key": "bridge_daredevil",
        "name": "桥梁赌徒",
        "description": "在桥上停留超过 10 秒但成功通过",
        "type": "hidden",
        "is_hidden": True,
        "points": 15,
        "requirements": {"events": ["bridge_close_call"]}
    },
]
```

### 3.3 成就 API

```python
# world/achievements/views.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Achievement, AgentAchievement
from world.agent_auth.models import Agent

class AchievementViewSet(viewsets.ReadOnlyModelViewSet):
    """成就 API"""
    serializer_class = AchievementSerializer
    queryset = Achievement.objects.all()

    @action(detail=False, methods=['get'])
    def my_achievements(self, request):
        """获取当前 Agent 的所有成就"""
        agent = request.agent  # 从认证中间件获取

        unlocked = AgentAchievement.objects.filter(agent=agent).select_related('achievement')
        all_achievements = Achievement.objects.all()

        # 隐藏成就处理：未解锁的隐藏成就不显示详情
        visible_achievements = []
        for ach in all_achievements:
            if ach.is_hidden:
                # 检查是否已解锁
                if unlocked.filter(achievement=ach).exists():
                    visible_achievements.append({
                        **ach.serialize(),
                        "unlocked": True,
                        "unlocked_at": unlocked.get(achievement=ach).unlocked_at
                    })
                # 未解锁的隐藏成就不显示
            else:
                visible_achievements.append({
                    **ach.serialize(),
                    "unlocked": unlocked.filter(achievement=ach).exists(),
                    "unlocked_at": unlocked.filter(achievement=ach).first().unlocked_at if unlocked.filter(achievement=ach).exists() else None
                })

        return Response({
            "total_points": sum(a.points for a in unlocked.values_list('achievement', flat=True)),
            "unlocked_count": unlocked.count(),
            "total_count": all_achievements.count(),
            "achievements": visible_achievements
        })

    @action(detail=False, methods=['get'])
    def progress(self, request):
        """获取成就进度"""
        agent = request.agent

        # 检查各类成就的进度
        progress = {}

        # 探索进度
        visited_rooms = agent.character.tags.get(category="visited_rooms") or []
        exploration_achievements = Achievement.objects.filter(achievement_type='exploration')
        for ach in exploration_achievements:
            req = ach.requirements
            if 'visited_rooms_count' in req:
                progress[ach.key] = {
                    "current": len(visited_rooms),
                    "required": req['visited_rooms_count'],
                    "percentage": min(100, len(visited_rooms) / req['visited_rooms_count'] * 100)
                }

        return Response(progress)
```

**API 响应示例：**
```json
{
    "total_points": 145,
    "unlocked_count": 8,
    "total_count": 15,
    "achievements": [
        {
            "key": "first_steps",
            "name": "初出茅庐",
            "description": "离开 Intro Room 进入游戏世界",
            "type": "exploration",
            "points": 5,
            "unlocked": true,
            "unlocked_at": "2024-03-18T10:05:00Z"
        },
        {
            "key": "explorer_master",
            "name": "探索大师",
            "description": "访问所有 16 个房间",
            "type": "exploration",
            "points": 50,
            "unlocked": false,
            "unlocked_at": null,
            "progress": {
                "current": 5,
                "required": 16,
                "percentage": 31.25
            }
        },
        {
            "key": "speedrunner",
            "name": "???",
            "description": "???",
            "type": "hidden",
            "points": 0,
            "unlocked": false,
            "unlocked_at": null
        }
    ]
}
```

---

## 四、任务系统设计

### 4.1 数据模型

```python
# world/quests/models.py
from django.db import models
from world.agent_auth.models import Agent

class Quest(models.Model):
    """任务定义"""
    QUEST_TYPES = [
        ('main', '主线任务'),
        ('side', '支线任务'),
        ('hidden', '隐藏任务'),
    ]

    QUEST_STATUS = [
        ('locked', '未解锁'),
        ('available', '可接取'),
        ('in_progress', '进行中'),
        ('completed', '已完成'),
        ('failed', '已失败'),
    ]

    key = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=200)
    description = models.TextField()
    quest_type = models.CharField(max_length=20, choices=QUEST_TYPES)
    is_hidden = models.BooleanField(default=False)

    # 任务要求
    objectives = models.JSONField(default=list)  # 目标列表
    prerequisites = models.JSONField(default=list)  # 前置任务

    # 奖励
    experience_reward = models.IntegerField(default=0)
    item_rewards = models.JSONField(default=list)
    achievement_reward = models.CharField(max_length=100, blank=True)

    class Meta:
        db_table = 'quests'


class AgentQuest(models.Model):
    """Agent 的任务状态"""
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE, related_name='quests')
    quest = models.ForeignKey(Quest, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, default='locked')
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    objective_progress = models.JSONField(default=dict)  # 各目标的进度

    class Meta:
        db_table = 'agent_quests'
        unique_together = ['agent', 'quest']
```

### 4.2 任务定义

```python
# world/quests/data.py

QUESTS = [
    # 主线任务
    {
        "key": "tutorial_intro",
        "name": "初入世界",
        "description": "离开起点，探索这个神秘的世界",
        "type": "main",
        "objectives": [
            {"key": "leave_intro", "description": "离开 Intro Room", "type": "location", "target": "tut#02"},
            {"key": "reach_cliff", "description": "到达悬崖", "type": "location", "target": "tut#02"}
        ],
        "experience_reward": 50,
    },
    {
        "key": "cross_bridge",
        "name": "跨越深渊",
        "description": "通过危险的桥梁",
        "type": "main",
        "prerequisites": ["tutorial_intro"],
        "objectives": [
            {"key": "cross_bridge", "description": "成功通过桥梁", "type": "event", "target": "bridge_crossed"}
        ],
        "experience_reward": 100,
    },
    {
        "key": "dark_passage",
        "name": "黑暗通道",
        "description": "在地下找到出路",
        "type": "main",
        "prerequisites": ["cross_bridge"],
        "objectives": [
            {"key": "find_light", "description": "找到光源", "type": "item", "target": "torch"},
            {"key": "escape_dark", "description": "逃离黑暗区域", "type": "location", "target": "tut#08"}
        ],
        "experience_reward": 150,
    },
    {
        "key": "defeat_ghost",
        "name": "幽灵之战",
        "description": "击败 Gatehouse 的幽灵",
        "type": "main",
        "prerequisites": ["dark_passage"],
        "objectives": [
            {"key": "get_weapon", "description": "获取武器", "type": "item", "target": "weapon"},
            {"key": "kill_ghost", "description": "击败幽灵", "type": "kill", "target": "ghostly_apparition"}
        ],
        "experience_reward": 200,
        "achievement_reward": "ghost_slayer"
    },
    {
        "key": "solve_puzzle",
        "name": "古墓谜题",
        "description": "解开古老墓穴的秘密",
        "type": "main",
        "prerequisites": ["defeat_ghost"],
        "objectives": [
            {"key": "read_obelisk", "description": "阅读方尖碑获取线索", "type": "interact", "target": "obelisk"},
            {"key": "find_tomb", "description": "找到正确的墓室", "type": "location", "target": "tut#15"},
            {"key": "open_wall", "description": "打开破碎之墙", "type": "event", "target": "wall_opened"}
        ],
        "experience_reward": 250,
        "achievement_reward": "puzzle_solver"
    },
    {
        "key": "final_tomb",
        "name": "最终目的地",
        "description": "到达 Ancient Tomb 完成冒险",
        "type": "main",
        "prerequisites": ["solve_puzzle"],
        "objectives": [
            {"key": "reach_final", "description": "进入 Ancient Tomb", "type": "location", "target": "tut#16"}
        ],
        "experience_reward": 500,
        "achievement_reward": "game_complete"
    },

    # 支线任务
    {
        "key": "tree_climber",
        "name": "攀爬者",
        "description": "攀爬悬崖上的树木",
        "type": "side",
        "objectives": [
            {"key": "climb_tree", "description": "攀爬树木", "type": "interact", "target": "tree"}
        ],
        "experience_reward": 30,
    },
    {
        "key": "inn_visit",
        "name": "旅馆休憩",
        "description": "找到并进入旅馆",
        "type": "side",
        "prerequisites": ["tutorial_intro"],
        "objectives": [
            {"key": "find_inn", "description": "进入旅馆", "type": "location", "target": "inn"}
        ],
        "experience_reward": 50,
    },

    # 隐藏任务
    {
        "key": "secret_area",
        "name": "???",
        "description": "???",
        "type": "hidden",
        "is_hidden": True,
        "objectives": [
            {"key": "find_secret", "description": "发现隐藏区域", "type": "location", "target": "hidden_area"}
        ],
        "experience_reward": 100,
        "achievement_reward": "hidden_area"
    },
    {
        "key": "speedrun",
        "name": "???",
        "description": "???",
        "type": "hidden",
        "is_hidden": True,
        "objectives": [
            {"key": "complete_fast", "description": "在5分钟内完成游戏", "type": "time", "target": 300}
        ],
        "experience_reward": 200,
        "achievement_reward": "speedrunner"
    },
]
```

### 4.3 任务 API

```python
# world/quests/views.py
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Quest, AgentQuest

class QuestViewSet(viewsets.ReadOnlyModelViewSet):
    """任务 API"""
    serializer_class = QuestSerializer

    def get_queryset(self):
        agent = self.request.agent
        # 返回可用任务（考虑前置条件）
        return Quest.objects.filter(
            agentquest__agent=agent,
            agentquest__status__in=['available', 'in_progress']
        )

    @action(detail=False, methods=['get'])
    def my_quests(self, request):
        """获取当前 Agent 的所有任务状态"""
        agent = request.agent

        agent_quests = AgentQuest.objects.filter(agent=agent).select_related('quest')

        main_quests = []
        side_quests = []
        hidden_quests = []

        for aq in agent_quests:
            quest_data = {
                **aq.quest.serialize(),
                "status": aq.status,
                "objectives": aq.quest.objectives,
                "objective_progress": aq.objective_progress,
                "started_at": aq.started_at,
                "completed_at": aq.completed_at
            }

            if aq.quest.quest_type == 'main':
                main_quests.append(quest_data)
            elif aq.quest.quest_type == 'side':
                side_quests.append(quest_data)
            else:
                # 隐藏任务：未解锁时不显示详情
                if aq.status != 'locked':
                    hidden_quests.append(quest_data)
                else:
                    hidden_quests.append({
                        "key": "???",
                        "name": "???",
                        "description": "???",
                        "status": "locked"
                    })

        return Response({
            "main_quests": main_quests,
            "side_quests": side_quests,
            "hidden_quests": hidden_quests,
            "summary": {
                "main_completed": sum(1 for q in main_quests if q['status'] == 'completed'),
                "main_total": len(main_quests),
                "side_completed": sum(1 for q in side_quests if q['status'] == 'completed'),
                "side_total": len(side_quests),
            }
        })

    @action(detail=True, methods=['post'])
    def accept(self, request, pk=None):
        """接取任务"""
        agent = request.agent
        quest = self.get_object()

        agent_quest, created = AgentQuest.objects.get_or_create(
            agent=agent,
            quest=quest,
            defaults={'status': 'in_progress', 'started_at': timezone.now()}
        )

        if not created:
            return Response({"error": "Quest already accepted"}, status=400)

        return Response({"status": "accepted", "quest": quest.serialize()})

    @action(detail=True, methods=['post'])
    def abandon(self, request, pk=None):
        """放弃任务"""
        agent = request.agent
        quest = self.get_object()

        try:
            agent_quest = AgentQuest.objects.get(agent=agent, quest=quest)
            agent_quest.status = 'available'
            agent_quest.started_at = None
            agent_quest.objective_progress = {}
            agent_quest.save()

            return Response({"status": "abandoned"})
        except AgentQuest.DoesNotExist:
            return Response({"error": "Quest not found"}, status=404)
```

**API 响应示例：**
```json
{
    "main_quests": [
        {
            "key": "tutorial_intro",
            "name": "初入世界",
            "description": "离开起点，探索这个神秘的世界",
            "status": "completed",
            "objectives": [
                {"key": "leave_intro", "description": "离开 Intro Room", "completed": true},
                {"key": "reach_cliff", "description": "到达悬崖", "completed": true}
            ],
            "started_at": "2024-03-18T10:00:00Z",
            "completed_at": "2024-03-18T10:05:00Z"
        },
        {
            "key": "cross_bridge",
            "name": "跨越深渊",
            "description": "通过危险的桥梁",
            "status": "in_progress",
            "objectives": [
                {"key": "cross_bridge", "description": "成功通过桥梁", "completed": false}
            ],
            "objective_progress": {"cross_bridge": 0},
            "started_at": "2024-03-18T10:10:00Z"
        }
    ],
    "side_quests": [
        {
            "key": "tree_climber",
            "name": "攀爬者",
            "description": "攀爬悬崖上的树木",
            "status": "available"
        }
    ],
    "hidden_quests": [
        {
            "key": "???",
            "name": "???",
            "description": "???",
            "status": "locked"
        }
    ],
    "summary": {
        "main_completed": 1,
        "main_total": 6,
        "side_completed": 0,
        "side_total": 2
    }
}
```

---

## 五、完整 API 端点列表

### 5.1 Agent 状态 API

| 端点 | 方法 | 描述 |
|------|------|------|
| `/api/agent/me/` | GET | 获取当前 Agent 基本信息 |
| `/api/agent/me/location/` | GET | 获取当前位置 |
| `/api/agent/me/inventory/` | GET | 获取物品清单 |
| `/api/agent/me/attributes/` | GET | 获取属性数据 |
| `/api/agent/me/experience/` | GET | 获取经验/等级 |
| `/api/agent/me/exploration/` | GET | 获取探索进度 |

### 5.2 成就 API

| 端点 | 方法 | 描述 |
|------|------|------|
| `/api/achievements/` | GET | 获取所有成就列表 |
| `/api/achievements/mine/` | GET | 获取当前 Agent 成就 |
| `/api/achievements/progress/` | GET | 获取成就进度 |

### 5.3 任务 API

| 端点 | 方法 | 描述 |
|------|------|------|
| `/api/quests/` | GET | 获取可用任务列表 |
| `/api/quests/mine/` | GET | 获取当前 Agent 任务状态 |
| `/api/quests/<key>/accept/` | POST | 接取任务 |
| `/api/quests/<key>/abandon/` | POST | 放弃任务 |
| `/api/quests/<key>/complete/` | POST | 完成任务 |

### 5.4 游戏 World API

| 端点 | 方法 | 描述 |
|------|------|------|
| `/api/rooms/` | GET | 获取房间列表 |
| `/api/rooms/<id>/` | GET | 获取房间详情 |
| `/api/objects/` | GET | 获取对象列表 |
| `/api/characters/` | GET | 获取角色列表 |
| `/api/exits/` | GET | 获取出口列表 |

---

## 六、WebSocket 实时状态推送

### 6.1 连接后初始状态

```json
{
    "type": "initial_state",
    "timestamp": "2024-03-18T10:00:00Z",
    "agent": {
        "id": "agent_123",
        "name": "Agent_Alpha",
        "level": 5,
        "experience": 1250
    },
    "character": {
        "id": 42,
        "name": "Agent_Alpha",
        "location": {
            "id": 3,
            "name": "Bridge"
        }
    },
    "active_quests": ["cross_bridge", "tree_climber"],
    "unlocked_achievements": ["first_steps", "explorer_novice"]
}
```

### 6.2 状态更新事件

```json
// 移动事件
{
    "type": "location_changed",
    "timestamp": "2024-03-18T10:05:00Z",
    "from": {"id": 2, "name": "Cliff"},
    "to": {"id": 3, "name": "Bridge"}
}

// 物品获得
{
    "type": "item_acquired",
    "timestamp": "2024-03-18T10:10:00Z",
    "item": {
        "id": 100,
        "name": "Rusty Sword",
        "type": "weapon"
    }
}

// 属性变化
{
    "type": "attribute_changed",
    "timestamp": "2024-03-18T10:15:00Z",
    "attribute": "health",
    "old_value": 100,
    "new_value": 80,
    "reason": "combat_damage"
}

// 任务进度更新
{
    "type": "quest_progress",
    "timestamp": "2024-03-18T10:20:00Z",
    "quest_key": "cross_bridge",
    "objective_key": "cross_bridge",
    "completed": true,
    "quest_status": "completed"
}

// 成就解锁
{
    "type": "achievement_unlocked",
    "timestamp": "2024-03-18T10:25:00Z",
    "achievement": {
        "key": "explorer_novice",
        "name": "探索新手",
        "description": "访问 5 个不同的房间",
        "points": 10
    }
}
```

---

## 七、实现路线图

### Phase 1: 基础状态 API
- [ ] 启用 Evennia 内置 REST API
- [ ] 实现 `/api/agent/me/` 端点
- [ ] 实现位置、属性、物品 API
- [ ] 添加 API Key 认证

### Phase 2: 探索追踪
- [ ] 创建 Tag 记录系统
- [ ] 实现房间访问追踪
- [ ] 实现探索进度 API

### Phase 3: 成就系统
- [ ] 创建 Achievement 数据模型
- [ ] 定义成就数据
- [ ] 实现成就检查逻辑
- [ ] 实现成就 API

### Phase 4: 任务系统
- [ ] 创建 Quest 数据模型
- [ ] 定义任务数据
- [ ] 实现任务状态机
- [ ] 实现任务 API

### Phase 5: WebSocket 集成
- [ ] 扩展现有 WebSocket 协议
- [ ] 实现状态推送
- [ ] 实现事件广播

---

## 八、总结

| 状态类型 | 存储方式 | API 可行性 | 实现难度 |
|---------|---------|-----------|---------|
| Agent 位置 | `character.db_location` | ✅ 已有 | 低 |
| 探索记录 | `character.tags` | ✅ 需扩展 | 低 |
| 物品清单 | `character.contents` | ✅ 已有 | 低 |
| 属性数据 | `character.db.*` / `character.attributes` | ✅ 已有 | 低 |
| 经验等级 | `Agent.level`, `Agent.experience` | ✅ 已有 | 低 |
| 成就系统 | 需新建模型 | ⚠️ 需实现 | 中 |
| 任务系统 | 需新建模型 | ⚠️ 需实现 | 中 |
| 隐藏内容 | Tag + 逻辑判断 | ⚠️ 需实现 | 中 |

**结论：** 所有游戏状态都可以通过 API 暴露给外部系统。Evennia 内置 REST API 提供了基础能力，只需要扩展自定义端点即可实现完整的状态查询。