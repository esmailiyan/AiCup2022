from enum import Enum

class MapType(Enum):
    def __str__(self) -> str:
        return str(self.value)

    EMPTY = 0
    AGENT = 1
    GOLD = 2
    TREASURY = 3
    WALL = 4
    FOG = 5
    OUT_OF_SIGHT = 6
    OUT_OF_MAP = 7