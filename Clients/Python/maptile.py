from maptype import MapType

class MapTile:
    def __init__(self) -> None:
        self.type: MapType
        self.data: int
        self.address: tuple(int, int)

    def __str__(self) -> str:
        res = self.type.name
        if self.type in [MapType.OUT_OF_SIGHT, MapType.OUT_OF_MAP]:
            return res.center(16)
        elif self.type in [MapType.AGENT, MapType.GOLD]:
            res += f':{self.data}'
        res += f' ({self.address[0]},{self.address[1]})'
        return res.center(16)