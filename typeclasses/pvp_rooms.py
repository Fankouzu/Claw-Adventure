from evennia.contrib.tutorials.evadventure.rooms import EvAdventurePvPRoom


class BrokenShoreRingRoom(EvAdventurePvPRoom):
    pass


def _broken_shore_pre_object_receive(self, arriving_object, source_location, **kwargs):
    if getattr(arriving_object, "key", "").strip().lower() == "ghostly apparition":
        arriving_object.msg("The ghost cannot cross into the ring.")
        return False
    return True


setattr(BrokenShoreRingRoom, "at_pre_object_receive", _broken_shore_pre_object_receive)
