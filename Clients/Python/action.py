from enum import Enum

class Action(Enum):
    def __str__(self) -> str:
        return str(self.value)

    STAY = 0
    MOVE_DOWN = 1
    MOVE_UP = 2
    MOVE_RIGHT = 3
    MOVE_LEFT = 4
    UPGRADE_DEFENCE = 5
    UPGRADE_ATTACK = 6
    LINEAR_ATTACK_DOWN = 7
    LINEAR_ATTACK_UP = 8
    LINEAR_ATTACK_RIGHT = 9
    LINEAR_ATTACK_LEFT = 10
    RANGED_ATTACK = 11