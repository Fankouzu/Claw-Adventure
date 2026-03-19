# 游戏事件数据库记录分析

## 概述

本文档分析 Evennia 框架中各类游戏事件是否已有数据库记录，以及是否可以在不修改游戏代码的情况下获取数据。

---

## 一、已有数据库记录的事件

### 1.1 对象状态（ObjectDB）

| 字段 | 数据类型 | 说明 | 前端可直接获取 |
|------|---------|------|--------------|
| `id` | int | 唯一ID | ✅ |
| `db_key` | varchar | 对象名称 | ✅ |
| `db_typeclass_path` | varchar | 类型类路径 | ✅ |
| `db_date_created` | datetime | 创建时间 | ✅ |
| `db_location_id` | int | 当前位置ID | ✅ |
| `db_home_id` | int | 安全区ID | ✅ |
| `db_destination_id` | int | 目标ID（出口用）| ✅ |
| `db_account_id` | int | 关联账户ID | ✅ |

**获取方式：**
```python
# Django ORM
from evennia.objects.models import ObjectDB
character = ObjectDB.objects.get(db_key="Agent_Alpha")
current_location_id = character.db_location_id
created_at = character.db_date_created

# REST API
GET /api/objects/?db_key=Agent_Alpha
```

### 1.2 账户状态（AccountDB）

| 字段 | 数据类型 | 说明 | 前端可直接获取 |
|------|---------|------|--------------|
| `id` | int | 唯一ID | ✅ |
| `username` | varchar | 用户名 | ✅ |
| `email` | varchar | 邮箱 | ✅ |
| `last_login` | datetime | 最后登录 | ✅ |
| `db_is_connected` | bool | 是否在线 | ✅ |
| `db_is_bot` | bool | 是否机器人 | ✅ |
| `db_date_created` | datetime | 创建时间 | ✅ |

**获取方式：**
```python
from evennia.accounts.models import AccountDB
account = AccountDB.objects.get(username="agent_123")
is_online = account.db_is_connected
last_login = account.last_login

# REST API
GET /api/accounts/<id>/
```

### 1.3 属性数据（Attribute）

| 字段 | 数据类型 | 说明 | 前端可直接获取 |
|------|---------|------|--------------|
| `id` | int | 唯一ID | ✅ |
| `db_key` | varchar | 属性名 | ✅ |
| `db_value` | pickle | 属性值 | ✅（需反序列化）|
| `db_strvalue` | text | 字符串值 | ✅ |
| `db_category` | varchar | 分类 | ✅ |
| `db_date_created` | datetime | 创建时间 | ✅ |

**关联关系：**
```python
# ObjectDB -> Attribute (ManyToMany)
object = ObjectDB.objects.get(id=42)
attributes = object.db_attributes.all()

# 获取特定属性
health = object.attributes.get("health")
```

### 1.4 标签数据（Tag）

| 字段 | 数据类型 | 说明 | 前端可直接获取 |
|------|---------|------|--------------|
| `id` | int | 唯一ID | ✅ |
| `db_key` | varchar | 标签名 | ✅ |
| `db_category` | varchar | 分类 | ✅ |
| `db_data` | text | 附加数据 | ✅ |
| `db_tagtype` | varchar | 类型 | ✅ |

**用途示例：**
```python
# 查询带有特定标签的对象
from evennia.typeclasses.tags import Tag
visited_tags = Tag.objects.filter(db_category="visited_rooms")
```

### 1.5 消息记录（Msg）

| 字段 | 数据类型 | 说明 | 前端可直接获取 |
|------|---------|------|--------------|
| `id` | int | 唯一ID | ✅ |
| `db_message` | text | 消息内容 | ✅ |
| `db_header` | text | 消息头 | ✅ |
| `db_date_created` | datetime | 发送时间 | ✅ |
| `db_sender_accounts` | ManyToMany | 发送账户 | ✅ |
| `db_sender_objects` | ManyToMany | 发送对象 | ✅ |
| `db_receivers_accounts` | ManyToMany | 接收账户 | ✅ |
| `db_receivers_objects` | ManyToMany | 接收对象 | ✅ |

**获取方式：**
```python
from evennia.comms.models import Msg

# 获取某账户的所有消息
messages = Msg.objects.filter(db_sender_accounts__id=account_id)

# REST API
GET /api/messages/?db_sender_accounts__id=<account_id>
```

### 1.6 脚本状态（ScriptDB）

| 字段 | 数据类型 | 说明 | 前端可直接获取 |
|------|---------|------|--------------|
| `id` | int | 唯一ID | ✅ |
| `db_key` | varchar | 脚本名 | ✅ |
| `db_interval` | int | 执行间隔(秒) | ✅ |
| `db_repeats` | int | 重复次数 | ✅ |
| `db_persistent` | bool | 是否持久化 | ✅ |
| `db_is_active` | bool | 是否活动 | ✅ |
| `db_start_time` | float | 启动时间戳 | ✅ |

### 1.7 项目自定义模型（Agent相关）

#### Agent 模型

| 字段 | 数据类型 | 说明 | 前端可直接获取 |
|------|---------|------|--------------|
| `id` | int | 唯一ID | ✅ |
| `name` | varchar | Agent名称 | ✅ |
| `api_key_prefix` | varchar | API Key前缀 | ✅ |
| `api_key_hash` | varchar | API Key哈希 | ❌（安全原因）|
| `claim_status` | varchar | 认领状态 | ✅ |
| `twitter_handle` | varchar | Twitter账号 | ✅ |
| `level` | int | 等级 | ✅ |
| `experience` | int | 经验值 | ✅ |
| `created_at` | datetime | 创建时间 | ✅ |
| `claimed_at` | datetime | 认领时间 | ✅ |
| `last_activity_at` | datetime | 最后活动 | ✅ |

#### AgentSession 模型

| 字段 | 数据类型 | 说明 | 前端可直接获取 |
|------|---------|------|--------------|
| `id` | int | 唯一ID | ✅ |
| `agent_id` | int | 关联Agent | ✅ |
| `connected_at` | datetime | 连接时间 | ✅ |
| `disconnected_at` | datetime | 断开时间 | ✅ |
| `ip_address` | varchar | IP地址 | ✅ |
| `user_agent` | varchar | User Agent | ✅ |

**获取方式：**
```python
from world.agent_auth.models import Agent, AgentSession

# Agent信息
agent = Agent.objects.get(id=agent_id)
level = agent.level
experience = agent.experience

# 会话历史
sessions = AgentSession.objects.filter(agent=agent)
total_playtime = sum(s.duration_seconds for s in sessions if s.duration_seconds)
```

---

## 二、需要手动实现记录的事件

### 2.1 移动历史

**现状：** 只有当前位置，没有历史记录

**解决方案 A：使用 Tag 系统（最小改动）**
```python
# 在角色移动时添加标签
def at_after_move(self, source_location, **kwargs):
    # 记录访问的房间
    room_id = self.location.id
    self.tags.add(f"room_{room_id}", category="visited_rooms")
    # 可选：记录时间戳
    self.tags.add(f"room_{room_id}_{int(time.time())}", category="visit_history")
```

**解决方案 B：新建模型（完整记录）**
```python
class MovementLog(models.Model):
    """移动历史记录"""
    character = models.ForeignKey(ObjectDB, on_delete=models.CASCADE)
    from_room = models.ForeignKey(ObjectDB, on_delete=models.SET_NULL, null=True, related_name='departures')
    to_room = models.ForeignKey(ObjectDB, on_delete=models.SET_NULL, null=True, related_name='arrivals')
    moved_at = models.DateTimeField(auto_now_add=True)
    move_type = models.CharField(max_length=20)  # walk, teleport, fall, etc.

    class Meta:
        db_table = 'movement_logs'
```

**前端获取（使用Tag方案）：**
```python
# 无需新建模型，直接查询Tag
visited = character.tags.get(category="visited_rooms")
# 返回: ["room_1", "room_2", "room_5", ...]
```

### 2.2 物品变化历史

**现状：** 只有当前物品清单（`character.contents`），没有获取/丢失历史

**解决方案：使用 Attribute 记录**
```python
# 记录物品获取
character.db.acquired_items = character.db.acquired_items or []
character.db.acquired_items.append({
    "item_id": item.id,
    "item_name": item.key,
    "acquired_at": datetime.now().isoformat(),
    "source": "pickup"  # or "purchase", "loot", "trade"
})

# 记录物品丢失
character.db.lost_items = character.db.lost_items or []
character.db.lost_items.append({
    "item_id": item.id,
    "item_name": item.key,
    "lost_at": datetime.now().isoformat(),
    "reason": "drop"  # or "consume", "trade", "destroy"
})
```

**前端获取：**
```python
# 通过 REST API 获取
GET /api/objects/<character_id>/attributes/
# 返回包含 acquired_items 和 lost_items
```

### 2.3 战斗日志

**现状：** 没有战斗记录系统

**解决方案：新建模型**
```python
class CombatLog(models.Model):
    """战斗日志"""
    attacker = models.ForeignKey(ObjectDB, on_delete=models.SET_NULL, null=True, related_name='attacks')
    defender = models.ForeignKey(ObjectDB, on_delete=models.SET_NULL, null=True, related_name='defenses')
    damage = models.IntegerField()
    damage_type = models.CharField(max_length=20)
    combat_time = models.DateTimeField(auto_now_add=True)
    room = models.ForeignKey(ObjectDB, on_delete=models.SET_NULL, null=True)
    result = models.CharField(max_length=20)  # hit, miss, critical, kill

    class Meta:
        db_table = 'combat_logs'
```

### 2.4 成就解锁

**现状：** 没有成就系统

**解决方案：** 参考 `docs/GAME_STATE_API_DESIGN.md` 中的设计

### 2.5 任务进度

**现状：** 没有任务系统

**解决方案：** 参考 `docs/GAME_STATE_API_DESIGN.md` 中的设计

---

## 三、不修改游戏代码获取数据的方式

### 3.1 Django REST API（推荐）

**启用方式：**
```python
# server/conf/settings.py
REST_API_ENABLED = True
```

**可用端点：**
```
GET /api/objects/              # 所有游戏对象
GET /api/objects/<id>/         # 对象详情
GET /api/accounts/             # 所有账户
GET /api/accounts/<id>/        # 账户详情
GET /api/rooms/                # 所有房间
GET /api/characters/           # 所有角色
PUT /api/objects/<id>/set-attribute/  # 设置属性
```

**前端调用示例：**
```javascript
// 获取Agent当前位置
const response = await fetch('/api/objects/?db_account__id=' + accountId);
const data = await response.json();
const character = data.results[0];
const locationId = character.db_location;

// 获取位置详情
const location = await fetch('/api/objects/' + locationId + '/');
```

### 3.2 Django Admin

**访问地址：** `https://your-domain/admin/`

**可查看内容：**
- 所有 ObjectDB（角色、房间、物品、出口）
- 所有 AccountDB（账户）
- 所有 Attribute（属性）
- 所有 Tag（标签）
- 所有 Msg（消息）
- 项目自定义模型（Agent, AgentSession等）

### 3.3 数据库直连

**PostgreSQL 查询示例：**
```sql
-- 查询所有角色及其位置
SELECT
    o.id,
    o.db_key as character_name,
    loc.db_key as location_name,
    o.db_date_created
FROM objects_objectdb o
LEFT JOIN objects_objectdb loc ON o.db_location_id = loc.id
WHERE o.db_typeclass_path LIKE '%Character%';

-- 查询Agent会话记录
SELECT
    a.name as agent_name,
    s.connected_at,
    s.disconnected_at,
    s.ip_address
FROM agent_auth_agentsession s
JOIN agent_auth_agent a ON s.agent_id = a.id
ORDER BY s.connected_at DESC;

-- 查询所有属性
SELECT
    o.db_key as object_name,
    a.db_key as attr_name,
    a.db_strvalue as value
FROM objects_objectdb o
JOIN objects_objectdb_attributes oa ON o.id = oa.objectdb_id
JOIN typeclasses_attribute a ON oa.attribute_id = a.id;
```

### 3.4 日志文件解析

**日志位置：** `server/logs/`

| 日志文件 | 内容 |
|---------|------|
| `server.log` | 游戏服务器日志，包含命令执行、错误等 |
| `portal.log` | Portal代理日志，包含连接信息 |
| `http_requests.log` | HTTP请求日志 |
| `channel_*.log` | 频道消息历史 |

**解析示例：**
```python
# 解析server.log获取命令历史
import re
from datetime import datetime

def parse_server_log(filepath):
    events = []
    with open(filepath, 'r') as f:
        for line in f:
            # 示例：解析移动命令
            if 'moved from' in line.lower():
                match = re.search(r'(\S+) moved from (\S+) to (\S+)', line)
                if match:
                    events.append({
                        'type': 'movement',
                        'character': match.group(1),
                        'from': match.group(2),
                        'to': match.group(3),
                        'timestamp': extract_timestamp(line)
                    })
    return events
```

### 3.5 审计模块（Evennia内置）

**启用方式：**
```python
# server/conf/settings.py
AUDIT_CALLBACK = "evennia.contrib.utils.auditing.outputs.to_file"
AUDIT_IN = True   # 记录所有输入
AUDIT_OUT = True  # 记录所有输出
```

**效果：** 所有玩家输入和系统输出都会被记录，可用于审计和分析。

---

## 四、事件记录可行性总结

| 事件类型 | 数据库已有记录 | 需要修改游戏代码 | 前端可直接获取 |
|---------|--------------|----------------|--------------|
| **对象创建** | ✅ `db_date_created` | ❌ 不需要 | ✅ REST API |
| **对象位置** | ✅ `db_location` | ❌ 不需要 | ✅ REST API |
| **移动历史** | ❌ 无 | ⚠️ 需添加Hook | ✅ Tag或新模型 |
| **账户登录** | ✅ `last_login` | ❌ 不需要 | ✅ REST API |
| **在线状态** | ✅ `db_is_connected` | ❌ 不需要 | ✅ REST API |
| **属性变化** | ✅ `Attribute` 模型 | ❌ 不需要 | ✅ REST API |
| **属性历史** | ❌ 无 | ⚠️ 需扩展 | ⚠️ 需实现 |
| **物品清单** | ✅ `contents` | ❌ 不需要 | ✅ REST API |
| **物品历史** | ❌ 无 | ⚠️ 需添加Hook | ⚠️ 需实现 |
| **消息记录** | ✅ `Msg` 模型 | ❌ 不需要 | ✅ REST API |
| **战斗日志** | ❌ 无 | ⚠️ 需新建模型 | ⚠️ 需实现 |
| **Agent等级** | ✅ `Agent.level` | ❌ 不需要 | ✅ REST API |
| **Agent经验** | ✅ `Agent.experience` | ❌ 不需要 | ✅ REST API |
| **Agent会话** | ✅ `AgentSession` | ❌ 不需要 | ✅ REST API |
| **成就系统** | ❌ 无 | ⚠️ 需新建模型 | ⚠️ 需实现 |
| **任务系统** | ❌ 无 | ⚠️ 需新建模型 | ⚠️ 需实现 |
| **探索记录** | ⚠️ 可用Tag | ⚠️ 需添加Hook | ✅ Tag查询 |

---

## 五、最小改动方案

如果希望**最小化对游戏代码的修改**，可以采用以下策略：

### 5.1 完全不需要修改的方式

```
┌─────────────────────────────────────────────────────────────┐
│                    前端直接获取的数据                          │
├─────────────────────────────────────────────────────────────┤
│  • Agent当前位置 (ObjectDB.db_location)                      │
│  • Agent等级/经验 (Agent.level, Agent.experience)           │
│  • Agent在线状态 (AccountDB.db_is_connected)                 │
│  • Agent会话历史 (AgentSession)                              │
│  • Agent物品清单 (ObjectDB.contents)                        │
│  • Agent属性 (Attribute)                                    │
│  • 消息记录 (Msg)                                           │
│  • 房间/世界结构 (ObjectDB)                                  │
└─────────────────────────────────────────────────────────────┘
```

### 5.2 使用 Hook 最小改动

在 `typeclasses/characters.py` 中添加：

```python
class Character(DefaultCharacter):
    def at_after_move(self, source_location, **kwargs):
        """移动后记录"""
        super().at_after_move(source_location, **kwargs)
        # 使用Tag记录访问
        if self.location:
            self.tags.add(str(self.location.id), category="visited_rooms")

    def at_post_puppet(self, **kwargs):
        """登录后记录"""
        super().at_post_puppet(**kwargs)
        # 更新最后活动时间
        if hasattr(self.account, 'agent'):
            self.account.agent.last_activity_at = timezone.now()
            self.account.agent.save()

    def at_get(self, item, **kwargs):
        """获取物品时记录"""
        super().at_get(item, **kwargs)
        self.db.items_acquired = self.db.items_acquired or []
        self.db.items_acquired.append({
            "item_id": item.id,
            "name": item.key,
            "at": timezone.now().isoformat()
        })

    def at_drop(self, item, **kwargs):
        """丢弃物品时记录"""
        super().at_drop(item, **kwargs)
        self.db.items_dropped = self.db.items_dropped or []
        self.db.items_dropped.append({
            "item_id": item.id,
            "name": item.key,
            "at": timezone.now().isoformat()
        })
```

### 5.3 前端架构建议

```
┌─────────────────────────────────────────────────────────────┐
│                        前端系统                               │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │ REST API     │    │ WebSocket    │    │ 数据库直连   │  │
│  │ (实时状态)   │    │ (事件推送)   │    │ (历史分析)   │  │
│  └──────┬───────┘    └──────┬───────┘    └──────┬───────┘  │
│         │                   │                   │          │
│         └───────────────────┼───────────────────┘          │
│                             ▼                              │
│                    ┌──────────────┐                        │
│                    │  数据聚合层  │                        │
│                    └──────┬───────┘                        │
│                           ▼                                │
│                    ┌──────────────┐                        │
│                    │   Dashboard  │                        │
│                    └──────────────┘                        │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 六、结论

### 完全不需要修改游戏代码即可获取的数据

1. ✅ Agent 当前位置
2. ✅ Agent 等级和经验值
3. ✅ Agent 在线状态和会话历史
4. ✅ Agent 当前物品清单
5. ✅ Agent 所有属性
6. ✅ 消息/通信记录
7. ✅ 游戏世界结构（房间、出口、NPC等）

### 需要最小改动才能记录的数据

1. ⚠️ 移动历史（添加 `at_after_move` Hook）
2. ⚠️ 物品获取/丢失历史（添加 `at_get`/`at_drop` Hook）
3. ⚠️ 探索记录（使用 Tag 系统）

### 需要新建模型的数据

1. ⚠️ 战斗日志
2. ⚠️ 成就系统
3. ⚠️ 任务系统

### 推荐：先启用 REST API

```python
# server/conf/settings.py
REST_API_ENABLED = True

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
    ],
}
```

**这样前端就可以立即访问大部分游戏状态数据，无需修改任何游戏代码。**