import random
from arena.utils.random_utils import is_cell_in_bounds, is_walkable
from constants import *

"""
DONE: we craft only half of the arena and then mirror it to the other half.
TODO: fix issue with sizes smaller than 32 
"""

"""
Remember 
cell = (int, int) means (row, col) in a way (y,x)
"""

class Arena:
    """
    We are going to do all the logic in cells, the pixel management is done in the visualizer.
    """
    def __init__(self, height): # in pixels == cells? num_cells = width / cell_size
        # enforce height multiple of 16 
        if height % 16 != 0:
            raise ("height of arena needs to be a multiple of 16!!!")

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

        """POST GENERATION"""
        self.occupancy_grid = {} # dictionary of cells and ids of the troop inside of them (max one per cell) --> key: (row, col) value: id

    def generate_river(self):
        # center is always going to be in the middle of an even number of cells, but there isn't a precise one so we handle both 
        # first center found is lower center (between the two even)

        # remember higher center is lower center + 1 
        # so we have two systems that go from lower center - (height_of_river//2) to lower center + (height_of_river//2) and from lower center + 1 - (height_of_river//2) to lower center + 1 + (height_of_river//2)
        # we combine them into one loop
        lower_center = self.height//2
        for i in range(lower_center, (lower_center)+(self.height_of_river - 1) + 1): #  lower_center-(int(self.height_of_river//2) - 1), (lower_center+1)+(int(self.height_of_river//2) - 1) + 1)
            #print("lower center", i)
            for index in range(len(self.grid[i])):
                self.grid[i][index] = WATER

    def generate_tower(self,  
        base_size_width = 3,
        base_size_height = 3,
        distance_from_left = 3,
        distance_from_bottom = 5
        ):

        scaled_width = int(self.width/18*base_size_width)
        scaled_height = int(self.height/32*base_size_height)

        bottom_left = (int(self.width/18*distance_from_left), self.height-int(self.height/32*distance_from_bottom) - 1) # from the left, from the top

        for index_row in range(bottom_left[1]-scaled_height+1, bottom_left[1]+1):
            for index_col in range(bottom_left[0], bottom_left[0]+scaled_width):
                self.grid[index_row][index_col] = TOWER_P1
                #print("grid", index_row, index_col)

    def generate_towers(self):
        # king tower bottom side
        # 1/32 from the bottom
        # 7/18 from the left 
        # tower is 4x4 (4/18, 4/32)
        # we are searching for bottom left corner

        base_size_width = 4
        base_size_height = 4
        distance_from_left = 7
        distance_from_bottom = 1
        self.generate_tower(base_size_width, base_size_height, distance_from_left, distance_from_bottom)


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
        base_size_width = 3
        base_size_height = 3
        distance_from_left = 2
        distance_from_bottom = 5
        self.generate_tower(base_size_width, base_size_height, distance_from_left, distance_from_bottom)

        # princess right 
        base_size_width = 3
        base_size_height = 3
        distance_from_left = 13
        distance_from_bottom = 5
        self.generate_tower(base_size_width, base_size_height, distance_from_left, distance_from_bottom)
    
    def generate_path(self):
        # if passes on water create bridge
        pass

        # we need to connect the two princess towers to the king tower
        # then we connect the princess towers (the middle) to the river (and over it)

    def generate_mock_bridges(self, bridge_width=3):
        """
        ONLY FOR DEBUGGING WE ARE GOING TO REMOVE THIS LATER AND MAKE IT GOOD
        """
        # Approximate x-centers of the princess towers (distance_from_left + half width)
        # left: 2 + 1.5 => 3.5/18 of width | right: 13 + 1.5 => 14.5/18 of width
        left_x  = int(self.width * (3.5 / 18.0))
        right_x = int(self.width * (14.5 / 18.0))

        lower_center = self.height // 2
        river_rows = range(lower_center, lower_center + self.height_of_river)
        half = bridge_width // 2

        for y in river_rows:
            for bx in (left_x, right_x):
                for x in range(bx - half, bx + half + 1):
                    if 0 <= x < self.width:
                        # Only overwrite river to make visible strips
                        if self.grid[y][x] == 2:
                            self.grid[y][x] = BRIDGE

    def mirror_arena(self):
        lower_center = self.height//2 
        print("lower center", lower_center)
        for row in range(lower_center, self.height):
            for col in range(self.width):
                if self.grid[row][col] == TOWER_P1:
                    self.grid[self.height-row-1][col] = TOWER_P2
                else:
                    self.grid[self.height-row-1][col] = self.grid[row][col]

    def world_generation(self):
        self.generate_river()
        self.generate_towers()
        self.generate_mock_bridges()
        self.mirror_arena()
    
    """utils"""
    def is_placable_cell(self, row, col, team):
        if not is_cell_in_bounds((row, col), self.grid):
            return False
        if not is_walkable(row, col, self.grid):
            return False
        if team == 1 and row < self.height//2 + self.height_of_river: # first half of the arena
            return False
        if team == 2 and row > self.height//2 - self.height_of_river: # second half of the arena
            return False
        
        return True

    def spawn_unit(self, troop, cell: (int, int)):
        if not is_cell_in_bounds(cell, self.grid):
            return False

        if cell in self.occupancy_grid:
            print("Error cell already occupied")
            return False
        
        if self.grid[cell[0]][cell[1]] in walkable_cells:
            self.occupancy_grid[cell] = troop
            troop.location = (cell[0], cell[1])
            troop.arena = self 
            return True

        print("Not placable cell")
        return False
    
    def move_unit(self, troop, new_cell: (int, int)):
        """
        Used to move a troop from old cell in the occupancy_grid
        """
        if not is_cell_in_bounds(new_cell, self.grid):
            return False
            
        if new_cell in self.occupancy_grid:
            # Cell is occupied by another troop
            return False

        if self.grid[new_cell[0]][new_cell[1]] in walkable_cells:
            self.occupancy_grid.pop(troop.location)
            self.occupancy_grid[new_cell] = troop
            troop.location = new_cell
            return True
            
        else:
            print("Not in walkable cells so can't move")
            return False
        

if __name__ == "__main__":
    arena = Arena(1600) 
    arena.world_generation()
