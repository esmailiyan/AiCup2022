from maptile import MapTile
from maptype import MapType

class Map:
    def __init__(self) -> None:
        self.width: int
        self.height: int
        self.gold_count: int
        self.sight_range: int
        self.grid: list
        self.fogs = []
        self.golds: list
        self.enemies: list
        self.empties: list
        self.treasury = []
        self.mines = []
        self.available_tiles: list
        self.adjmatrix: dict
        self.data: list

    def __str__(self) -> str:
        res = f'sight range -> {self.sight_range}\n'
        for i in range(self.sight_range):
            res += '\t'
            for j in range(self.sight_range):
                res += str(self.grid[i * self.sight_range + j])
                res += '*' if j < self.sight_range-1 else '\n'
        return res[:-1]

    def set_default_info(self) -> None:
        self.golds = []
        self.enemies = []
        self.empties = []
        self.available_tiles = []
        self.adjmatrix = {}
        self.data = [[0 for _ in range(20)] for _ in range(20)]

    def set_tile_info(self, tile) -> None:
        if tile.type == MapType.EMPTY:
            self.empties.append(tile.address)
        elif tile.type == MapType.AGENT:
            self.enemies.append(tile.address)
            self.data[tile.address[0]][tile.address[1]] = tile.data
        elif tile.type == MapType.GOLD:
            self.golds.append(tile.address)
            self.data[tile.address[0]][tile.address[1]] = tile.data
        elif tile.type == MapType.TREASURY:
            if tile.address not in self.treasury:
                self.treasury.append(tile.address)
        elif tile.type == MapType.WALL:
            if tile.address not in self.mines:
                self.mines.append(tile.address)
        elif tile.type == MapType.FOG:
            if tile.address not in self.fogs:
                self.fogs.append(tile.address)

        if tile.type in [MapType.EMPTY,MapType.GOLD,MapType.TREASURY,MapType.FOG]:
            self.available_tiles.append(tile.address)

    def set_adjacency_matrix(self, location) -> None:
        self.available_tiles.append(location)

        for tile in self.available_tiles:
            self.adjmatrix[tile] = []
            if (tile[0]+1,tile[1]) in self.available_tiles:    self.adjmatrix[tile].append((tile[0]+1,tile[1]))
            if (tile[0]-1,tile[1]) in self.available_tiles:    self.adjmatrix[tile].append((tile[0]-1,tile[1]))   
            if (tile[0],tile[1]+1) in self.available_tiles:    self.adjmatrix[tile].append((tile[0],tile[1]+1))  
            if (tile[0],tile[1]-1) in self.available_tiles:    self.adjmatrix[tile].append((tile[0],tile[1]-1)) 

    def set_grid_size(self) -> None:
        self.grid = [MapTile() for _ in range(self.sight_range ** 2)]