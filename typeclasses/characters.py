"""
Characters

Characters are (by default) Objects setup to be puppeted by Accounts.
They are what you "see" in game. The Character class in this module
is setup to be the "default" character type created by the default
creation commands.

"""

from evennia.objects.objects import DefaultCharacter

from .objects import ObjectParent


# class Character(ObjectParent, DefaultCharacter):
#     """
#     The Character just re-implements some of the Object's methods and hooks
#     to represent a Character entity in-game.

#     See mygame/typeclasses/objects.py for a list of
#     properties and methods available on all Object child classes like this.

#     """

#     pass
"""
Characters

这是所有角色的底层躯壳蓝图。
"""
from evennia.contrib.tutorials.evadventure.characters import EvAdventureCharacter
from evennia.contrib.tutorials.evadventure.combat_twitch import TwitchCombatCmdSet

class Character(EvAdventureCharacter):
    """
    魔改版：继承官方高级躯壳，并强行植入战斗芯片！
    """
    def at_object_creation(self):
        # 先执行官方的初始化（生成血条、蓝条、属性等）
        super().at_object_creation()

        # 【核心黑科技】：给所有新生儿的大脑里永久挂载即时战斗（Twitch Combat）指令包！
        self.cmdset.add(TwitchCombatCmdSet, persistent=True)