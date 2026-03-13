"""
Characters

This is the customized Character class for the Zero-Player Sandbox.
It inherits from EvAdventureCharacter to get health/stats, 
adds the Twitch Combat command set at creation, 
and teleports the character to the Combat Arena upon login.
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
        super().at_object_creation()
        # 焊死即时战斗芯片
        self.cmdset.add(TwitchCombatCmdSet, persistent=True)

    def at_post_puppet(self, **kwargs):
        """
        当玩家/AI的“灵魂”（Account）附体到“躯壳”（Character）上时触发。
        注意：在 Evennia 中，角色的登录钩子是 at_post_puppet，而不是 at_post_login。
        """
        super().at_post_puppet(**kwargs)
        
        # 强行空投：通过系统内置别名或名字寻找竞技场，防 ID 变更
        arena = search_object("evtechdemo#01") or search_object("Combat Arena") or search_object("#10")
        if arena and self.location != arena[0]:
            self.move_to(arena[0], quiet=True, move_hooks=False)
            # 传送到新地方后，强行看一眼四周刷新视野
            self.execute_cmd("look")
