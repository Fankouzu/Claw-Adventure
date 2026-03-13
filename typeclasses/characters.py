"""
Characters

This is the customized Character class for the Zero-Player Sandbox.
It inherits from EvAdventureCharacter to get health/stats, 
adds the Twitch Combat command set at creation, 
and teleports the character to the Combat Arena (#10) upon login.
"""

from evennia.contrib.tutorials.evadventure.characters import EvAdventureCharacter
from evennia.contrib.tutorials.evadventure.combat_twitch import TwitchCombatCmdSet
from evennia import search_object

class Character(EvAdventureCharacter):
    """
    魔改版：零玩家沙盒专属角斗士躯壳。
    高内聚：自带战斗芯片 + 自动空投进角斗场。
    """
    def at_object_creation(self):
        # 1. 拿官方的初始血条和属性
        super().at_object_creation()
        # 2. 焊死即时战斗芯片 (Twitch Combat)
        self.cmdset.add(TwitchCombatCmdSet, persistent=True)

    def at_post_login(self, session=None, **kwargs):
        # 3. 执行常规的登录逻辑
        super().at_post_login(session, **kwargs)
        
        # 4. 【核心黑科技】：强制空投！
        # 不管它出生在哪，只要一登录，瞬间把它拽进 #10 角斗场
        arena = search_object("#10")
        if arena and self.location != arena[0]:
            self.move_to(arena[0], quiet=True, move_hooks=False)
