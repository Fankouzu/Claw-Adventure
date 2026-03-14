"""
Characters

This is the customized Character class for the Claw-Jianghu universe.
"""

from evennia.contrib.tutorials.evadventure.characters import EvAdventureCharacter
from evennia.contrib.tutorials.evadventure.combat_twitch import TwitchCombatCmdSet

class Character(EvAdventureCharacter):
    """
    继承版躯壳：保留基础的属性和战斗模块，但移除强制空投逻辑。
    恢复玩家自由探索世界的权利。
    """
    def at_object_creation(self):
        super().at_object_creation()
        # 依然保留即时战斗指令集，以防未来用到
        self.cmdset.add(TwitchCombatCmdSet, persistent=True)
        
    # 【已清理】删除了 at_post_puppet 里的强制空投逻辑。
    # 现在角色登录后，将老老实实呆在系统默认的出生点（Limbo）或上次下线的位置。
