# Evennia Tutorial World 完整攻略

## 概述

Evennia Tutorial World 是一个16房间的单人解谜冒险游戏，设计目的是展示 Evennia 框架的功能特性。

**安装方式：**
```python
# 以超级用户(#1)登录后执行
batchcommand contrib.tutorials.tutorial_world.build
```

**游玩准备：**
- 使用 `quell` 命令降低权限为普通玩家身份
- 超级用户会跳过某些检查，影响游戏体验
- 若角色在 **Limbo**（传送门房间），出口一般为 **`adventure`**。进入 **Intro** 后，离开到悬崖的出口在 `build.ev` 里是 **`begin adventure` / `begin` / `start`**，不是 `north`/`n`
- **吊桥 (BridgeRoom)** 没有普通出口，靠房间上的 **`east`/`e`**（多步）穿过；不是 `north`/`n`
- **`search` / `feel` / `feel around`** 是 **DarkRoom** 里对 `look` 的别名，只在暗牢等黑暗房间有效；在别处输入会落到账号层并出现 nomatch

---

## 游戏地图结构（16个房间）

```
                    [隐藏区域 ?]
                         │
                    [Ancient Tomb] (tut#16) - 最终目标
                         │
    [Intro] ──► [Cliff] ──► [Bridge] ──► … ──► [Gatehouse] ──► …
    (tut#01)    (tut#02)    (tut#05)           (tut#09)      (tut#10+)
    可选: Cliff 爬树后 `north` → [Outside Inn] (tut#03) 等支线
                   │
              [Inn] (可选)
```

### 房间详细列表

| 房间号 | 名称 | 类型 | 描述 |
|--------|------|------|------|
| tut#01 | Intro Room | IntroRoom | 游戏入口，设置玩家属性 |
| tut#02 | Cliff | WeatherRoom | 悬崖，有天气系统，可攀爬树木 |
| tut#03 | Outside Evennia Inn 等 | WeatherRoom | 爬树解锁 `north` 后的隐藏路径相关区域（见 `build.ev`） |
| tut#04 | Evennia Inn | TutorialRoom | 旅店室内等（批次文件顺序以你库为准） |
| tut#05 | The old bridge | BridgeRoom | 吊桥，多步 `east`/`west` |
| tut#06 | Protruding ledge | WeatherRoom | 桥上坠落落点（非主暗房谜题） |
| tut#07 | Underground passages | TutorialRoom | 地下通道枢纽 |
| tut#08 | Dark cell | DarkRoom | 暗牢；`feel`/`search` 等黑暗交互在此类房间 |
| tut#09 | Ruined gatehouse | TutorialRoom | 过桥后东门楼 |
| tut#10+ | Inner wall / courtyard / … | 多种 | 城堡废墟巡逻区等 |
| tut#10-15 | Tombs | TutorialRoom | 墓室群，需要找到正确的墓室 |
| tut#16 | Ancient Tomb | TutorialRoom | 古老墓穴，最终目标 |

---

## 主线任务攻略

### 任务一：离开起点 (Intro Room)

**目标：** 离开 Intro Room 进入悬崖区域

**步骤：**
1. 使用 `look` 查看周围环境
2. 阅读提示信息（文案会提示写 **`begin`** 开始任务）
3. 使用 **`begin`**、**`start`** 或完整短语 **`begin adventure`** 离开 Intro（与 `contrib.tutorials.tutorial_world.build` 里悬崖入口的 exit 别名一致）

**技术说明：** IntroRoom 会自动设置玩家属性，包括权限和初始状态。

---

### 任务二：探索悬崖 (Cliff)

**目标：** 找到进入下一区域的方法

**步骤：**
1. `look` 观察环境 - 你会看到一个悬崖和一棵树
2. `climb tree` 攀爬树木 - 这会设置一个标签(tag)
3. 观察天气变化 - WeatherRoom 会随机显示不同天气信息

**隐藏路径：** 攀爬树木后可以进入一个隐藏区域（通过标签系统实现）

**提示：** 仔细阅读所有描述，寻找可交互的对象。

---

### 任务三：通过危险之桥 (Bridge)

**目标：** 安全通过桥梁而不掉落

**房间机制：** BridgeRoom 是一个特殊的房间，模拟大型空间需要多步穿越；**没有普通出口**，由房间 CmdSet 提供 **`east`/`west`**。

**步骤：**
1. 在悬崖 (Cliff) 用 **`east`**（或 **`e`** / **`bridge`**）进入桥房间
2. `look` 观察桥的状态（桥上有定制的 `look`，并有概率坠落）
3. 连续多次 **`east`** 走到东端（默认需 **5 次** `east` 从西岸入口走到出口），直至进入门楼一侧
4. **警告：** 每次 `look` 在西半段桥上有小概率坠落；weather ticker 也会刷氛围——不要误以为卡死

**失败惩罚：** 坠落会进 **暗牢 (Dark cell)** 等区域（以你世界里的 `build.ev` / dbref 为准）

**技术实现：** `tutorial_bridge_position` 计数 + `CmdEast`/`CmdWest`；与「用 `n` 快速连穿」不是同一机制。

---

### 任务四：地下通道 (Underground Passage)

**目标：** 在黑暗中找到出路

**步骤：**
1. `look` - 你会看到一片漆黑
2. 搜索周围 - `search` 或 `feel around`
3. 寻找光源 - LightSource 物品

**DarkRoom 机制：**
- 在没有光源的情况下，大部分描述不可见
- 找到光源后可以正常查看环境
- 光源有使用时限，会自动燃尽消失
- **教程实现说明：** 全黑时房间本体可能被加上 `view:false()` 一类锁，普通 `look` **看不到房间描述**（甚至可能出现 “could not view” 类提示），这是 Evennia 教程的**故意设计**，不是服务器损坏。请用 `feel`、`search` 等黑暗专用交互，拿到光源并 `light` / 点燃后再 `look`。

**牢房逃脱 (Dark Cell)：**
如果在桥上掉落，会进入牢房：
1. 检查牢房结构
2. 寻找弱点或隐藏出口
3. 使用特定命令逃脱

**Agent 测试注意：** 在 Dark Cell 或仍处于「全黑 cmdset」时不要指望常规 `look` 房间；先解决光源与黑暗交互，再判断是否真有 bug。

---

### 任务五：门房与怪物 (Gatehouse)

**目标：** 避开或击败巡逻的怪物

**区域描述：** Gatehouse 有敌对生物巡逻（Ghostly apparition - 幽灵幻影）

**怪物属性：**
- 名称：Ghostly apparition（幽灵幻影）
- 描述：带有雾状触手的幽灵
- 状态循环：巡逻 → 狩猎 → 攻击

**策略一：潜行通过**
1. 等待怪物巡逻到其他房间
2. 快速移动到下一区域
3. 避免进入怪物视野

**策略二：战斗**
1. 首先需要找到武器（见任务六）
2. 使用 `kill` 或 `attack` 命令
3. 使用武器命令 `stab` 或 `slash`

**怪物AI机制：**
- 巡逻状态：在房间间移动
- 狩猎状态：发现玩家后追踪
- 攻击状态：进入战斗
- 死亡后会自动复活

---

### 任务六：获取武器

**目标：** 找到能够战斗的武器

**位置：** Temple 区域的武器架

**步骤：**
1. 进入 Temple 区域
2. 找到 Weapon Rack（武器架）
3. `get weapon` 或类似命令获取武器

**武器系统：**
- TutorialWeapon 提供战斗命令
- 可用命令：`stab`（刺）和 `slash`（砍）
- 伤害和命中率随机计算
- 武器原型由 WEAPON_PROTOTYPES 定义

**武器架机制：** 使用 spawner 系统，可以生成随机武器。

---

### 任务七：神庙谜题 (Temple)

**目标：** 解开神庙中的谜题

**步骤：**
1. `look` 观察神庙结构
2. 找到 Obelisk（方尖碑）
3. `read obelisk` 或 `look obelisk` 获取线索

**Obelisk 机制：**
- 每次观察会随机显示不同的描述
- 提供前往正确墓室的线索
- 线索会指向特定的墓室入口

**注意：** 方尖碑的描述会变化，可能需要多次查看。

---

### 任务八：寻找正确的墓室 (Tombs)

**目标：** 根据线索找到正确的墓室

**区域结构：** 多个墓室相连（tut#10 到 tut#15）

**步骤：**
1. 根据 Obelisk 的线索选择方向
2. 进入对应墓室
3. 如果选择错误，会被传送到惩罚区域

**TeleportRoom 机制：**
- 检查玩家属性
- 根据检查结果决定是否传送
- 错误选择可能导致回到起点或进入牢房

**正确路径：** 需要 trial and error 或仔细分析线索

---

### 任务九：破碎之墙谜题 (Crumbling Wall)

**目标：** 打开隐藏通道

**位置：** **Courtyard（庭院，教程地图中约为 tut#12）** — 破碎之墙是房间里的一个物体，不是全局命令。

**前提：**
- 房间必须 **有光**（教程里通过 `location.db.is_lit` 等逻辑控制）。人在 **Dark Cell**、地下全黑区域或未点亮光源时，墙上的 **shift 类指令不会出现在 cmdset**，会出现 `Command not available` —— 这通常是 **谜题状态** 而非代码缺失。
- 先确保身处 **已点亮的庭院**，再对墙操作。

**步骤：**
1. `look wall` 查看墙壁（若提示不可用，先解决光照/房间）
2. 注意墙壁上不同颜色的根须
3. `shift <color> down` / `shift <color> root` 等（以墙上说明为准）移动根须
4. 正确的顺序会露出按钮
5. `push button` 按下按钮打开通道

**CrumblingWall 机制：**
- 这是一个复杂的谜题出口
- 需要特定顺序的操作
- 颜色可能包括：red（红）、blue（蓝）、green（绿）等
- 指令挂在 **墙对象** 的 cmdset 上，且受 **房间是否明亮** 影响

**提示：** 仔细观察墙壁描述，颜色顺序很重要！

---

### 任务十：最终目标 - Ancient Tomb (tut#16)

**目标：** 到达古老墓穴，完成游戏

**步骤：**
1. 通过破碎之墙进入
2. 进入 Ancient Tomb
3. 找到宝藏/完成条件

**OutroRoom 机制：**
- 自动清理玩家的临时属性
- 重置游戏状态
- 显示完成信息

---

## 支线任务

### 支线一：旅馆休息 (Inn)

**位置：** 从悬崖区域可以进入

**步骤：**
1. 在悬崖区域寻找隐藏路径
2. 进入旅馆
3. 与环境交互

**奖励：** 可能获得额外信息或物品

---

### 支线二：隐藏区域 (?)

**位置：** 需要查看代码发现

**触发条件：**
1. 攀爬悬崖上的树
2. 设置特定标签
3. 进入隐藏传送点

**技术实现：** 通过 tag 系统控制访问权限

---

## 隐藏任务

### 隐藏任务一：探索者成就

**触发条件：** 访问所有16个房间

**步骤：**
1. 确保访问每个房间至少一次
2. 包括牢房（故意在桥上失败）
3. 包括隐藏区域

---

### 隐藏任务二：无伤通关

**目标：** 不被怪物攻击完成游戏

**策略：**
1. 避开 Gatehouse 的怪物
2. 快速通过危险区域
3. 不触发任何陷阱

---

### 隐藏任务三：光源大师

**目标：** 在光源燃尽前完成黑暗区域

**挑战：** LightSource 有时间限制

---

## 游戏机制详解

### 1. 房间类型系统

| 类型类 | 功能 |
|--------|------|
| IntroRoom | 设置玩家属性，游戏入口 |
| OutroRoom | 清理属性，游戏出口 |
| WeatherRoom | 显示随机天气消息 |
| BridgeRoom | 多步穿越，超时惩罚 |
| DarkRoom | 黑暗环境，需要光源 |
| TutorialRoom | 基础房间，支持帮助命令 |
| TeleportRoom | 传送谜题，属性检查 |

### 2. 物品类型系统

| 类型类 | 功能 |
|--------|------|
| TutorialObject | 基础物品，支持重置 |
| TutorialReadable | 可阅读物品 |
| TutorialClimbable | 可攀爬物品，设置标签 |
| Obelisk | 方尖碑，随机线索 |
| LightSource | 光源，计时器控制 |
| CrumblingWall | 谜题墙壁，多步解锁 |
| TutorialWeapon | 武器，提供战斗命令 |
| TutorialWeaponRack | 武器架，生成随机武器 |

### 3. 怪物AI系统 (Mob)

**状态机：**
```
[空闲] ──发现玩家──► [巡逻] ──追踪──► [狩猎] ──接触──► [攻击]
   ▲                                              │
   └──────────────丢失目标/死亡────────────────────┘
```

**行为：**
- 巡逻：在房间间移动
- 狩猎：追踪玩家
- 攻击：造成伤害
- 自动复活：死亡后重生

### 4. 战斗系统

**命令：**
- `kill <target>` - 开始战斗
- `stab <target>` - 刺击
- `slash <target>` - 砍击

**伤害计算：**
- 命中率随机
- 伤害值随机
- 怪物有伤害抗性

---

## 完整通关流程（快速版）

```
1. [Intro] ──► 向北离开
          │
2. [Cliff] ──► climb tree（可选，解锁隐藏区域）
          │
3. [Bridge] ──► 快速向北通过（不要停留！）
          │
4. [Underground] ──► 找到光源
          │
5. [Dark Area] ──► 在黑暗中找到出路
          │
6. [Gatehouse] ──► 避开或击败怪物（需要武器）
          │
7. [Temple] ──► get weapon from rack ──► read obelisk
          │
8. [Tombs] ──► 根据线索选择正确墓室
          │
9. [Crumbling Wall] ──► shift roots in order ──► push button
          │
10. [Ancient Tomb] ──► 完成游戏！
```

---

## 失败情况与恢复

### 掉落桥下
- **后果：** 传送到 Dark Cell
- **恢复：** 寻找牢房出口，回到地下通道

### 被怪物杀死
- **后果：** 可能需要从头开始
- **注意：** 怪物会自动复活

### 选择错误墓室
- **后果：** 传送回起点或牢房
- **恢复：** 重新根据线索选择

### 光源燃尽
- **后果：** 在黑暗中无法看清环境
- **恢复：** 摸索找到新光源或出口

---

## 技术实现要点

### 批处理构建 (build.ev)
```
# 等价于在游戏中输入一系列命令
create tut#01:IntroRoom
set tut#01,desc "..."
# ... 更多构建命令
```

### 标签系统
- 用于隐藏区域的访问控制
- `climb tree` 设置特定标签
- TeleportRoom 检查标签决定传送

### Ticker 系统
- WeatherRoom：定时发送天气消息
- BridgeRoom：超时检测
- Mob：定时移动和攻击

### 属性系统
- IntroRoom 设置初始属性
- 游戏过程中更新
- OutroRoom 清理临时属性

---

## 附录：常用命令

### 基础命令
| 命令 | 功能 |
|------|------|
| look | 查看环境 |
| north/n, south/s, east/e, west/w | 移动 |
| get <item> | 拾取物品 |
| drop <item> | 丢弃物品 |
| inventory/i | 查看背包 |
| help | 查看帮助 |

### 交互命令
| 命令 | 功能 |
|------|------|
| read <object> | 阅读物品 |
| climb <object> | 攀爬 |
| search | 搜索 |
| push <object> | 推动 |
| shift <object> | 移动/调整 |

### 战斗命令
| 命令 | 功能 |
|------|------|
| kill <target> | 攻击目标 |
| stab <target> | 刺击（需要武器）|
| slash <target> | 砍击（需要武器）|
| flee | 逃跑 |

### 调试命令（超级用户）
| 命令 | 功能 |
|------|------|
| quell | 降低权限 |
| unquell | 恢复权限 |
| teleport <location> | 传送 |
| examine <object> | 检查对象 |

---

## 总结

Evennia Tutorial World 是一个精心设计的教程游戏，展示了以下技术特性：

1. **自定义房间类型** - 通过继承实现特殊行为
2. **状态机AI** - Mob的智能行为
3. **谜题系统** - 多步解锁和条件检查
4. **时间系统** - Ticker实现延时和周期事件
5. **属性管理** - 玩家状态追踪
6. **批处理构建** - 自动化世界创建

通关关键：
- 仔细阅读所有描述
- 快速通过危险区域
- 获取武器再战斗
- 记住Obelisk的线索
- 正确操作Crumbling Wall