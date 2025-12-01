from ast import Raise
from multiprocessing import Value
from arena.utils.creation import generate_tower, generate_river, generate_mock_bridges, mirror_arena
from arena.utils.random_utils import is_cell_in_bounds, is_walkable
from constants import *


"""
DONE: we craft only half of the arena and then mirror it to the other half
"""

"""
Remember 
cell = (int, int) means (row, col) in a way (y,x)
"""

class Arena:
    """Fun fact: We are going to do all the logic in cells, the pixel management is done in the visualizer"""

    def __init__(self, height): # in pixels == cells? num_cells = width / cell_size
        """
        Initializes arena grid, towers, and bookkeeping structures

        - Time: Worst case = Average case = O(h * w) 
                where h is height and w is width
        - Space: O(h * w) for the grid storage
        """
        # safety checks
        if MULTIPLIER_GRID_HEIGHT <= 0:
            raise ValueError("MULTIPLIER_GRID_HEIGHT must be greater than 0")
        # enforce height multiple of 16 and at least 32
        if height % 16 != 0 and height >= 32:
            # because we can't modify from here the constant MULTIPLIER_GRID_HEIGHT we don't want to continue this loop with this bad values so we raise an error
            raise ValueError("height of arena needs to be a multiple of 16!!! and bigger or equal than 32")

        self.height = height
        self.width = int(height/16 * 9) # ratio of width to height

        print("initializing arena with sizes", self.height, self.width)

        # scale height of river too
        self.height_of_river = 1 # because we are mirroring the arena this is going to be dobled
        self.height_of_river = self.height_of_river * int(height/32)

        """
        Each cell:
        - 0: empty
        - 1: grass (floor)
        - 2: water --> we also place water where the towers are supposed to be.
        - 3: bridge
        """
        # default is grass
        self.grid = [[GRASS for _ in range(self.width)] for _ in range(self.height)]
        self.towers_P1 = {} # dict key: tower_n value: tower_obj
        self.towers_P2 = {}
        self.game_finished = False


        """POST GENERATION"""
        self.occupancy_grid = {} # dictionary of cells and ids of the troop inside of them (max one per cell) --> key: (row, col) value: id
        self.occupancy_grid_flying = {} # dictionary of cells and ids of the troop inside of them (max one per cell) --> key: (row, col) value: id
        self.unique_troops = set()
        self.frame_count = 0

        self.asset_manager = None
        self.arena_background_dirty = True

        self.one_minute = TICKS_PER_SECOND*60
        self.time_left = self.one_minute*3 # the match is supposed to be 3 minutes

        self.elixir_multiplier = 1.0

    def generate_towers(self):
        """
        Generates all player one towers in their base positions

        - Time: Worst case = Average case O(t * (tw * th)) 
                where t is number of towers (3), tw/th are tower width/height
        - Space: O(1) additional - because it modifies existing grid in place
        """
        # king tower bottom side
        # 1/32 from the bottom
        # 7/18 from the left 
        # tower is 4x4 (4/18, 4/32)
        # we are searching for bottom left corner

        distance_from_left = 7
        distance_from_bottom = 1
        generate_tower(self.width, self.height, self, self.asset_manager, 0, 1, distance_from_left, distance_from_bottom)

        # princes towers bottom side
        # left tower bottom left corner is
        # * 2 from the left
        # * 5 grom the bottom 
        # * size is 3x3 (3/32, 3/18)
        
        # right botttom RIGHT princess is:
        # * 2 away from the right (13/18 from the left)
        # * 5 from the bottom 
        # * size is 3x3 (3/32, 3/18)

        # princess left
        distance_from_left = 2
        distance_from_bottom = 5
        generate_tower(self.width, self.height, self, self.asset_manager, -1, 1, distance_from_left, distance_from_bottom)

        # princess right 
        distance_from_left = 13
        distance_from_bottom = 5
        generate_tower(self.width, self.height, self, self.asset_manager, 1, 1, distance_from_left, distance_from_bottom)
    
    def world_generation(self):
        """
        Generates the full arena layout including river, towers, bridges, and mirroring

        - Time: Worst case = Average case = O(h * w) 
                river generation is O(river_h * w)
                towers O(constant) 
                bridges O(constant)
                mirroring O(h/2 * w)
        - Space: O(1) additional - because all operations modify existing grid
        """
        generate_river(self.height, self.height_of_river, self)
        self.generate_towers()
        generate_mock_bridges(self.width, self.height, self, self.height_of_river)
        mirror_arena(self.height, self.width, self, self.asset_manager)
    
    """utils""" 
    def tick(self):
        """
        Advances arena state by one frame and handles match timing logic

        - Time: Worst case = Average case = O(1)
        - Space: O(1)
        """
        self.frame_count += 1
        self.time_left -= 1
        if self.game_finished:
            return False

        if self.time_left == self.one_minute:
            print("1 minute left")
            self.elixir_multiplier = 2.0 # we double the elixir in the last minute
        
        if self.time_left <= 0:
            print("Match over")
            self.game_finished = True
            return False

        return True

    def is_movable_cell(self, row, col, moving_troop=None, is_flying=False):
        """
        Checks if a troop can move into a given cell

        - Time: Worst case = Average case = O(1) - because bounds check, grid lookup, and hash table lookup are all constant time.
        - Space: O(1)
        """
        if not is_cell_in_bounds((row, col), self.grid):
            return False

        if not is_walkable(row, col, self.grid, is_flying=is_flying):
                return False

        if moving_troop:
            occupancy_grid = moving_troop.get_occupancy_grid()
            if (row, col) in occupancy_grid and moving_troop != occupancy_grid[(row, col)]: # check if the cell is occupied by itself, this would mean it can move there
                return False  

        return True
    
    def is_placable_cell(self, row, col, team, moving_troop=None, is_flying=False):
        """
        Checks if a troop can be placed on a given cell for a specific team

        - Time: Worst case = Average case = O(1) - because constant time checks on bounds, grid value, hash table, and tower dictionary.
        - Space: O(1)
        """
        if not is_cell_in_bounds((row, col), self.grid):
            return False
        if not is_walkable(row, col, self.grid, is_flying=is_flying): # air troops shouldn't be able to be placed on water cells so we pass is_flying=False in the calling method, they will be able to move on it but shouldn't be placed there
            return False

        if moving_troop:
            occupancy_grid = moving_troop.get_occupancy_grid()
            if (row, col) in occupancy_grid and moving_troop != occupancy_grid[(row, col)]: # check if the cell is occupied by itself, this would mean it can move there
                return False  

        opponent_towers = self.towers_P2 if team == 1 else self.towers_P1
    
        # check which princess towers are alive
        right_princess_alive = 1 in opponent_towers
        left_princess_alive = -1 in opponent_towers
        both_princesses_alive = right_princess_alive and left_princess_alive
        both_princesses_destroyed = not right_princess_alive and not left_princess_alive
        
        # calculate boundaries
        mid_height = self.height // 2
        river_height = self.height_of_river
        mid_width = self.width // 2
        
        # both princess towers destroyed: can place anywhere
        if both_princesses_destroyed:
            if team == 1:
                if row < self.height // 4:
                    return False
            else:
                if row > 3 * self.height // 4:
                    return False
            return True
        
        # both princess towers alive: restrict to own half
        if both_princesses_alive:
            if team == 1:
                # team 1 (bottom): can't place above river
                if row < mid_height + river_height:
                    return False
            else:  # team == 2
                # team 2 (top): can't place below river
                if row > mid_height - river_height:
                    return False
            return True
        
        # one princess tower destroyed: allow partial crossing
        if team == 1:
            if not right_princess_alive:
                # right princess destroyed: can place on right side after river, left side restricted
                if col < mid_width:
                    # left side: still restricted to own half
                    if row < mid_height + river_height:
                        return False
                else:
                    # right side: can place after quarter point
                    if row < self.height // 4:
                        return False
            else:  # left princess destroyed
                # left princess destroyed: can place on left side after river, right side restricted
                if col > mid_width:
                    # right side: still restricted to own half
                    if row < mid_height + river_height:
                        return False
                else:
                    # left side: can place after quarter point
                    if row < self.height // 4:
                        return False
        else:  # team == 2
            if not right_princess_alive:
                # right princess destroyed: can place on right side before river, left side restricted
                if col < mid_width:
                    # left side: still restricted to own half
                    if row > mid_height - river_height:
                        return False
                else:
                    # right side: can place before quarter point
                    if row > 3 * self.height // 4:
                        return False
            else:  # left princess destroyed
                # left princess destroyed: can place on left side before river, right side restricted
                if col > mid_width:
                    # right side: still restricted to own half
                    if row > mid_height - river_height:
                        return False
                else:
                    # left side: can place before quarter point
                    if row > 3 * self.height // 4:
                        return False

        # if both princess towers are alive: allowed cells are before the river
        
        return True

    def spawn_unit(self, troop, cell: (int, int)):
        """
        Spawns a troop into the arena and marks all occupied cells

        - Time: Worst case = Average case = O(tw * th) 
                where tw/th are troop width/height
        - Space: O(tw * th) for occupied cells dictionary entries.
        """
        if not is_cell_in_bounds(cell, self.grid):
            return False

        #scaled_width = max(1, int(self.width/18*troop.width//2))
        #scaled_height = max(1, int(self.height/32*troop.height//2))
    
        #troop.width = scaled_width
        #troop.height = scaled_height

        # so we set the location to the top left corner of the troop and arena in it 
        troop.location = cell
        troop.arena = self

        occupied_cells = troop.occupied_cells()
        # checking if all the other cells are valid   

        for occupied_cell in occupied_cells:
            if not self.is_placable_cell(occupied_cell[0], occupied_cell[1], troop.team, moving_troop=troop, is_flying=troop.troop_can_fly):
                return False
        
        for occupied_cell in occupied_cells:
            occupancy_grid = troop.get_occupancy_grid()
            occupancy_grid[occupied_cell] = troop # we set the troop in all the cells it occupies
            
        self.unique_troops.add(troop)

        return True
    
    def move_unit(self, troop, new_cell: (int, int)):
        """
        Used to move a troop from old cell in the occupancy_grid.

        - Time: Worst case = Average case = O(tw * th) 
                where tw/th are troop width/height 
                because it iterates over occupied cells twice (old + new)
        - Space: O(tw * th) for temporary occupied cells dictionaries
        """
        if not is_cell_in_bounds(new_cell, self.grid):
            return False
        
        old_location = troop.location # we save the old location to move it back later
        troop.location = new_cell  # temporarily set to calculate occupied cells
        new_occupied_cells = troop.occupied_cells()
        troop.location = old_location  # we move it back to the old location
        
        for cell in new_occupied_cells:
            if not self.is_movable_cell(cell[0], cell[1], moving_troop=troop, is_flying=troop.troop_can_fly):
                return False
        
        old_occupied_cells = troop.occupied_cells()

        occupancy_grid = troop.get_occupancy_grid()

        for cell in old_occupied_cells:
            if cell in occupancy_grid and occupancy_grid[cell] == troop: # kind of unecessary double check but better be safe
                occupancy_grid.pop(cell)


        troop.location = new_cell # to the new left top corner

        for cell in new_occupied_cells:
            occupancy_grid[cell] = troop # we set the troop in all the cells it occupies
        
    
        return True

    def remove_unit(self, troop):
        """
        Remove a troop from the occupancy grid (clean up all cells it occupies).

        - Time: Worst case = Average case = O(tw * th) 
                where tw/th are troop width/height
        - Space: O(1) - because it just modifies existing structures
        """
        if troop in self.unique_troops:
            self.unique_troops.remove(troop)
        occupied_cells = troop.occupied_cells()
        for cell in occupied_cells:
            occupancy_grid = troop.get_occupancy_grid()
            if cell in occupancy_grid and occupancy_grid[cell] == troop: # kind of unecessary double check but better be safe
                occupancy_grid.pop(cell)
        return True
    
    def remove_tower(self, tower_troop):
        """
        Remove a tower from the occupancy grid (clean up all cells it occupies).

        - Time: Worst case = Average case = O(tw * th)
                where tw/th are tower width/height (looping over occupied cells)
        - Space: O(tw * th) for the occupied_cells collection
        """

        towers = self.towers_P1 if tower_troop.team == 1 else self.towers_P2 
        # before we were using self.unique_troops but we can use the towers_P1 and towers_P2 dictionaries
        # now we use O(1) lookup time instead of O(n)
        if 0 in towers and tower_troop.tower_number != 0: # if it is 0 we are destroying the king tower so no need to activate it
            if not towers[0].is_active and towers[0].is_alive:
                towers[0].is_active = True

        self.unique_troops.discard(tower_troop)
        occupied_cells = tower_troop.occupied_cells()
        if tower_troop.team == 1:
            self.towers_P1.pop(tower_troop.tower_number)
        else:
            self.towers_P2.pop(tower_troop.tower_number)
        
        for cell in occupied_cells:
            # clean up occupancy_grid
            if cell in self.occupancy_grid and self.occupancy_grid[cell] == tower_troop:
                self.occupancy_grid.pop(cell)
            
            # clean up grid for towers
            row, col = cell
            if is_cell_in_bounds(cell, self.grid):
                # reset tower cells back to GRASS
                if self.grid[row][col] in [TOWER_P1, TOWER_P2, TOWER_P1+1, TOWER_P2+1, TOWER_P1-1, TOWER_P2-1]:
                    self.grid[row][col] = GRASS
        
        self.arena_background_dirty = True
        if 0 not in self.towers_P1:
            self.game_finished = True
            return False
        if 0 not in self.towers_P2:
            self.game_finished = True # meaning stop game
            return False # the return is not used but it is for visual purposes

        return True

if __name__ == "__main__":
    arena = Arena(1600) 
    arena.world_generation()
