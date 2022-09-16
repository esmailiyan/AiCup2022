from os import makedirs
from enum import Enum
from action import Action
from maptype import MapType
from maptile import MapTile
from map import Map

DEBUG = 0

class GameState:
    def __init__(self) -> None:
        self.rounds = int(input())
        self.def_upgrade_cost = int(input())
        self.atk_upgrade_cost = int(input())
        self.cool_down_rate = float(input())
        self.linear_attack_range = int(input())
        self.ranged_attack_radius = int(input())
        self.map = Map()
        self.map.width, self.map.height = map(int, input().split())
        self.map.gold_count = int(input())
        self.map.sight_range = int(input())  # equivalent to (2r+1)
        self.map.set_grid_size()
        self.debug_log = ''
        self.last_wallets = None
        self.attack_values = [0,0,0,0]
        self.last_path = []
        self.watched = []
        self.target = (-1,-1)

    def set_info(self) -> None:
        self.location = tuple(map(int, input().split()))  # (row, column)
        self.last_path.append(self.location)
        self.map.set_default_info()
        for tile in self.map.grid:
            tile.type, tile.data, *tile.address = map(int, input().split())
            tile.type = MapType(tile.type)
            tile.address = tuple(tile.address)
        self.agent_id = int(input())  # player1: 0,1 --- player2: 2,3
        self.current_round = int(input())  # 1 indexed
        self.attack_ratio = float(input())
        self.deflvl = int(input())
        self.atklvl = int(input())
        self.wallet = int(input())
        self.safe_wallet = int(input())
        self.wallets = [*map(int, input().split())]  # current wallet
        self.last_action = int(input())  # -1 if unsuccessful
        self.team = [0, 1] if self.agent_id in [0, 1] else [2, 3]

        for tile in self.map.grid:
            if self.target == tile.address and self.last_action == -1 and tile.type == MapType.FOG and self.distance(self.location,tile.address) == 1:
                tile.type = MapType.WALL
                self.log('Debug (msg)', 'fogs change to wall')
                self.log('Debug (tile.address)', str(tile.address))
                self.log('Debug (tile.type)', str(tile.type))
                self.log('Debug (target)', str(self.target))
                if len(self.map.fogs) and tile.address in self.map.fogs:    
                    self.map.fogs.remove(tile.address)
                    self.log('Debug', 'remove tile from fogs')
            elif len(self.map.mines) and tile.address in self.map.mines and tile.type == MapType.FOG:     
                tile.type = MapType.WALL
                self.log('Debug', 'type fogs change to wall - (address in mines)')
            self.map.set_tile_info(tile)
        self.map.set_adjacency_matrix(self.location)

    def debug(self) -> None:
        self.debug_log += f'{60 * "-"}\n'

    def log(self, title, text) -> None:
        self.debug_log += f'{title}: {text}\n'

    def debug_file(self) -> None:
        fileName = '../logs/'
        makedirs(fileName, exist_ok=True)
        fileName += f'AGENT{self.agent_id}.log'
        with open(fileName, 'w') as f:
            f.write(self.debug_log)

    def distance(self, a, b) -> int:
        return abs(a[0]-b[0]) + abs(a[1]-b[1])

    def move(self, target) -> Action:

        self.log(title='Target', text=str(target))

        if self.location[0] < target[0] and (self.location[0]+1, self.location[1]) in self.map.adjmatrix[self.location]:    
            self.target = (self.location[0]+1, self.location[1])
            return Action.MOVE_DOWN
        if self.location[0] > target[0] and (self.location[0]-1, self.location[1]) in self.map.adjmatrix[self.location]:    
            self.target = (self.location[0]-1, self.location[1])
            return Action.MOVE_UP
        if self.location[1] > target[1] and (self.location[0], self.location[1]-1) in self.map.adjmatrix[self.location]:    
            self.target = (self.location[0], self.location[1]-1)
            return Action.MOVE_LEFT
        if self.location[1] < target[1] and (self.location[0], self.location[1]+1) in self.map.adjmatrix[self.location]:    
            self.target = (self.location[0], self.location[1]+1)
            return Action.MOVE_RIGHT

        self.log(title='Move', text='Stay')

        return Action.STAY

    def get_merit(self, node) -> int:
        merit: int = 0
        for i in range(self.map.height):
            for j in range(self.map.width):
                if self.distance((i,j), node) <= (self.map.sight_range-1)/2 and (i,j) not in self.watched:
                    merit += 1
        return merit

    def way_to(self, target, parent):
        way = []
        node = target
        while parent[node] != -1:
            way.append(node)
            node = parent[node]
        way.reverse()
        return way

    def get_golds(self) -> tuple:
        # Define variables
        bfs = []
        marked = []
        parent = {}
        values = {}
        length = {}

        # Config start nodes
        bfs.append(self.location)
        values[self.location] = 0
        parent[self.location] = -1
        length[self.location] = 0

        # Start Dijkstra
        i = 0
        while i < len(bfs):
            node, new = bfs[i], False
            if node not in marked:
                marked.append(node)
                for child in self.map.adjmatrix[node]:
                    if child not in marked:
                        bfs.append(child)
                        parent[child] = node
                        length[child] = length[node] + 1
                        values[child] = values[node] + self.map.data[child[0]][child[1]] / length[child]
                        if child in self.map.golds:    
                            new = True
                if new:
                    bfs.sort(key=lambda node: [values[node], -length[node], -self.last_path.count(node)], reverse=True)
                    i = 0
                else:
                    i += 1
            else:
                i += 1

        # Find way
        way = self.way_to(target=bfs[0], parent=parent)

        # Retrun next move
        if len(way):    
            return way[0]
        elif len(self.map.adjmatrix[self.location]):    
            return self.map.adjmatrix[self.location][0]
        else:    
            return self.location

    def go_treasury(self) -> tuple:
        # Define variables
        bfs = []
        marked = []
        parent = {}
        values = {}
        length = {}

        # Config start nodes
        bfs.append(self.location)
        marked.append(self.location)
        values[self.location] = 0
        parent[self.location] = -1
        length[self.location] = 0

        # Start BFS
        for node in bfs:
            for v in self.map.adjmatrix[node]:
                if v not in marked:
                    bfs.append(v)
                    marked.append(v)
                    parent[v] = node
                    values[v] = values[node] + self.map.data[v[0]][v[1]]
                    length[v] = length[node] + 1

        bfs.sort(key=lambda tile: [min([self.distance(tile, trea) for trea in self.map.treasury]), -values[tile]])

        # Find way
        way = self.way_to(target=bfs[0], parent=parent)

        # Retrun next move
        if len(way):    
            return way[0]
        if len(self.map.adjmatrix[self.location]):    
            return self.map.adjmatrix[self.location][0]
        else:    
            return self.location

    def go_worthy(self, target) -> tuple:
        # Define variables
        bfs = []
        marked = []
        parent = {}
        values = {}
        length = {}

        # Config start nodes
        bfs.append(self.location)
        marked.append(self.location)
        values[self.location] = 0
        parent[self.location] = -1
        length[self.location] = 0

        # Start BFS
        for node in bfs:
            for v in self.map.adjmatrix[node]:
                if v not in marked:
                    bfs.append(v)
                    marked.append(v)
                    parent[v] = node
                    values[v] = values[node] + self.map.data[v[0]][v[1]]
                    length[v] = length[node] + 1

        # Sort BFS
        bfs.sort(key=lambda tile: [self.distance(tile, target), -values[tile]])

        # Find way
        way = self.way_to(target=bfs[0], parent=parent)

        # Retrun next move
        if len(way):    
            return way[0]
        if len(self.map.adjmatrix[self.location]):    
            return self.map.adjmatrix[self.location][0]
        else:     
            return self.location

    def select_worthy(self) -> tuple:
        # Define Variables
        merit = [[0 for _ in range(self.map.width)] for _ in range(self.map.height)]
        dist = [[0 for _ in range(self.map.width)] for _ in range(self.map.height)]
        nodes = []

        # Set merit & dist info
        for i in range(self.map.height):
            for j in range(self.map.width):
                if (i,j) not in self.map.mines and (i,j) not in self.map.enemies:    
                    nodes.append((i,j))
                merit[i][j] = self.get_merit((i,j))
                dist[i][j] = self.distance(self.location, (i,j))
        
        # Set target
        nodes.sort(key=lambda node: [merit[node[0]][node[1]], -dist[node[0]][node[1]], -self.last_path.count(node)], reverse=True)
        
        # Logs
        # self.log('merit', merit[nodes[0][0]][nodes[0][1]])
        # self.log('dist', dist[nodes[0][0]][nodes[0][1]])

        # Return Answer
        return nodes[0]

    def update_watched(self) -> None:
        for i in range(self.map.height):
            for j in range(self.map.width):
                if self.distance((i,j), self.location) <= (self.map.sight_range-1)/2 and (i,j) not in self.watched:
                    self.watched.append((i,j))

    def attack(self):
        attack_number = 3
        total_value_of_attack = 0
        for agent in self.map.enemies:
            agent_id = self.map.data[agent[0]][agent[1]]
            if  agent_id not in self.team and self.distance(self.location,agent)<=self.ranged_attack_radius:  total_value_of_attack+=self.attack_values[agent_id]
        if total_value_of_attack>= attack_number:   return Action.RANGED_ATTACK

        for agent in self.map.enemies:
            agent_id = self.map.data[agent[0]][agent[1]]
            if self.attack_values[agent_id]>=attack_number and agent_id not in self.team:
                if self.distance(self.location,agent)<=self.ranged_attack_radius:   
                    return Action.RANGED_ATTACK
            
                elif (agent[0]==self.location[0] or agent[1]==self.location[1]) and self.distance(self.location,agent)<=self.linear_attack_range:
                    in_same_row = agent[0]==self.location[0]
                    in_same_column = agent[1]==self.location[1]
                    global no_wall_in_way
                    no_wall_in_way = True
                    if in_same_row:
                        min_cloumn = min(agent[1],self.location[1])
                        max_cloumn = max(agent[1],self.location[1])
                        for i in range(min_cloumn+1,max_cloumn):
                            if (agent[0],i) in self.map.mines:
                                no_wall_in_way=False
                                break
                        if no_wall_in_way:
                            if max_cloumn == agent[1]:
                                return Action.LINEAR_ATTACK_RIGHT
                            return Action.LINEAR_ATTACK_LEFT
                    if in_same_column:
                        min_row = min(agent[0],self.location[0])
                        max_row = max(agent[0],self.location[0])
                        for i in range(min_row+1,max_row):
                            if (i,agent[1]) in self.map.mines:
                                no_wall_in_way=False
                                break
                        if no_wall_in_way:
                            if max_row == agent[0]:
                                return Action.LINEAR_ATTACK_DOWN
                            return Action.LINEAR_ATTACK_UP
        return -1

    def get_action(self) -> Action:
        # Analyze & Update
        self.update_watched()

        # Setting Attack Values:
        for id in range(0,4):
            self.attack_values[id] =  self.attack_ratio * (self.atklvl/(self.atklvl+1)) * self.wallets[id]

        # Sorting Enemies & Golds & Treasury & Adjmatrix:
        self.map.enemies.sort(key=lambda enemy: self.attack_values[self.map.data[enemy[0]][enemy[1]]])
        self.map.golds.sort(key=lambda gold: self.distance(self.location, gold))
        self.map.fogs.sort(key=lambda fog: self.distance(self.location, fog))
        self.map.treasury.sort(key=lambda tile: self.distance(self.location, tile))
        self.map.adjmatrix[self.location].sort(key=lambda adj: self.get_merit(adj))
        
        # Logs
        self.log('round', f'{str(self.current_round)}/{str(self.rounds)}')
        self.log('location', str(self.location))
        self.log('Map', str(self.map))
        # self.log('wallet', str(self.wallet))
        # self.log('adjmatrix', str(self.map.adjmatrix[self.location]))
        # self.log('worthy', self.select_worthy())
        self.log('Last Action', str(self.last_action))
        self.log('mins', str(self.map.mines))
        self.log('fogs', str(self.map.fogs))

        # Guidance
        '''go to treasurys --> return self.move(self.go_treasury())'''
        '''go to random adjs --> return self.move(self.map.adjmatrix[self.location][0])'''
        '''go to fogs --> return self.move(self.map.fogs[0])'''
        '''go to golds --> return self.move(self.get_golds())'''
        '''go to less-watched node --> return self.move(self.go_worthy(self.select_worthy()))'''

        #Setting Minimum & Maximum Of Wallet & Also Conditions Of Upgrade For Each Round
        remaining_rounds = self.rounds - self.current_round
        max_value_in_wallet = 6
        min_value_in_wallet = 0
        max_value_in_wallet = min(max_value_in_wallet,remaining_rounds//2.5)
        min_value_in_wallet = max(min_value_in_wallet,max_value_in_wallet-5)
        # self.log("Min Val",min_value_in_wallet)
        # self.log("Max Val",max_value_in_wallet)
        
        atk_upg_condition = remaining_rounds>=30 and self.atk_upgrade_cost<=4 and self.wallet>= self.atk_upgrade_cost and self.atklvl<4
        def_upg_condition = remaining_rounds>=40 and self.def_upgrade_cost<=4 and self.wallet>= self.def_upgrade_cost and self.deflvl<3
        treasury_dist_condition = self.distance(self.map.treasury[0],self.location)>=5 if len(self.map.treasury) else True
       
        # Algorithm
        if self.attack()!=-1: return self.attack()

        if self.wallet >= max_value_in_wallet and max_value_in_wallet!=0:
            if atk_upg_condition and treasury_dist_condition:   return Action.UPGRADE_ATTACK
            if def_upg_condition and treasury_dist_condition: return Action.UPGRADE_DEFENCE
            if len(self.map.treasury):                                  return self.move(self.go_treasury())
            elif self.move(self.go_worthy(self.select_worthy())):       return self.move(self.go_worthy(self.select_worthy()))

        elif self.wallet >= min_value_in_wallet:
            if len(self.map.golds):                                     return self.move(self.get_golds())
            elif len(self.map.treasury):                                return self.move(self.go_treasury())
            # elif len(self.map.fogs):                                    return self.move(self.map.fogs[0])
            elif self.move(self.go_worthy(self.select_worthy())):       return self.move(self.go_worthy(self.select_worthy()))

        else:
            if len(self.map.golds):                                     return self.move(self.get_golds())
            # elif len(self.map.fogs):                                    return self.move(self.map.fogs[0])
            elif self.move(self.go_worthy(self.select_worthy())):       return self.move(self.go_worthy(self.select_worthy()))

        # self.log("Action","No Action Found! Range Attack..")
        return Action.RANGED_ATTACK


if __name__ == '__main__':
    game_state = GameState()
    for _ in range(game_state.rounds):
        game_state.set_info()
        print(game_state.get_action())
        if DEBUG:
            game_state.debug()
    if DEBUG:
        game_state.debug_file()
