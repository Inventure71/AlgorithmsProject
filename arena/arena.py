import random
from arena.utils.random_utils import is_cell_in_bounds, is_walkable
from constants import *
from troops.generic_troop import Troop
import re
from arena.utils.random_utils import extract_tower_stats

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
        # enforce height multiple of 16 and at least 32
        if height % 16 != 0 and height >= 32:
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
        self.unique_troops = set()

        self.asset_manager = None

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
        tower_type, # -1, 0, 1 (left, middle, right)
        team,
        distance_from_left = 3,
        distance_from_bottom = 5
        ):

        if team == 1:
            tower_grid_type = TOWER_P1
        else:
            tower_grid_type = TOWER_P2
        
        # extract base stats
        troop_health, troop_damage, troop_movement_speed, troop_attack_type, troop_attack_speed, troop_attack_range, troop_attack_aggro_range, troop_attack_cooldown, troop_width, troop_height = extract_tower_stats(tower_type)
        
        # calculate scaled dimensions (these are the actual grid cell sizes)
        scaled_width = int(self.width/18*troop_width)
        scaled_height = int(self.height/32*troop_height)

        bottom_left = (int(self.width/18*distance_from_left), self.height-int(self.height/32*distance_from_bottom) - 1)
        top_left = (bottom_left[1]-scaled_height+1, bottom_left[0])
        
        # create tower with scaled dimensions (not base dimensions)
        tower = Troop(
            name=f"Tower {tower_type}",
            health=troop_health,
            damage=troop_damage,
            movement_speed=troop_movement_speed,
            attack_type=troop_attack_type,
            attack_speed=troop_attack_speed,
            attack_range=troop_attack_range,
            attack_aggro_range=troop_attack_aggro_range,
            attack_cooldown=troop_attack_cooldown,
            width=scaled_width,  
            height=scaled_height,  
            color="blue" if team == 1 else "red",
            team=team,
            location=top_left,
            arena=self,
            asset_manager=self.asset_manager
        )

        self.unique_troops.add(tower)

        # place tower in grid and occupancy_grid
        for index_row in range(bottom_left[1]-scaled_height+1, bottom_left[1]+1):
            for index_col in range(bottom_left[0], bottom_left[0]+scaled_width):
                self.grid[index_row][index_col] = tower_grid_type
                self.occupancy_grid[(index_row, index_col)] = tower
        
        return tower  # return the tower for potential use

    def generate_towers(self):
        # king tower bottom side
        # 1/32 from the bottom
        # 7/18 from the left 
        # tower is 4x4 (4/18, 4/32)
        # we are searching for bottom left corner

        distance_from_left = 7
        distance_from_bottom = 1
        self.generate_tower(0, 1, distance_from_left, distance_from_bottom)


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
        self.generate_tower(-1, 1, distance_from_left, distance_from_bottom)

        # princess right 
        distance_from_left = 13
        distance_from_bottom = 5
        self.generate_tower(1, 1, distance_from_left, distance_from_bottom)
    
    def generate_path(self):
        # if passes on water create bridge
        pass

        # we need to connect the two princess towers to the king tower
        # then we connect the princess towers (the middle) to the river (and over it)

    def generate_mock_bridges(self, bridge_width=3):
        """
        ONLY FOR DEBUGGING WE ARE GOING TO REMOVE THIS LATER AND MAKE IT GOOD
        """
        # Scale bridge width to match arena size (similar to tower scaling)
        scaled_bridge_width = int(self.width/18 * bridge_width)
        scaled_bridge_width = max(1, scaled_bridge_width)  # Ensure minimum width of 1
        
        # Approximate x-centers of the princess towers (distance_from_left + half width)
        # left: 2 + 1.5 => 3.5/18 of width | right: 13 + 1.5 => 14.5/18 of width
        left_x  = int(self.width * (3.5 / 18.0))
        right_x = int(self.width * (14.5 / 18.0))

        lower_center = self.height // 2
        river_rows = range(lower_center, lower_center + self.height_of_river)
        half = scaled_bridge_width // 2

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

        # store towers we've already processed
        processed_towers = set()
        
        for row in range(lower_center, self.height):
            for col in range(self.width):
                if self.grid[row][col] == TOWER_P1:
                    # get the tower from this cell
                    tower = self.occupancy_grid.get((row, col))
                    
                    if tower and tower not in processed_towers:
                        processed_towers.add(tower)

                        # extract tower type from name
                        result = re.search(r'Tower\s*(-?\d+)', tower.name)
                        if result:
                            tower_type = int(result.group(1))
                            
                            # dalculate mirrored position
                            orig_row, orig_col = tower.location
                            mirrored_row = self.height - (orig_row + tower.height)
                            mirrored_col = orig_col
                            
                            # create mirrored tower with correct team and color
                            mirrored_tower = Troop(
                                name=f"Tower {tower_type}",
                                health=tower.health,
                                damage=tower.damage,
                                movement_speed=0,
                                attack_type="Ranged",
                                attack_speed=tower.attack_speed,
                                attack_range=tower.attack_range,
                                attack_aggro_range=tower.attack_aggro_range,
                                attack_cooldown=tower.attack_cooldown,
                                width=tower.width,  
                                height=tower.height, 
                                color=(255, 0, 0),
                                team=2,
                                location=(mirrored_row, mirrored_col),
                                arena=self,
                                asset_manager=self.asset_manager
                            )
                            
                            # place mirrored tower in occupancy_grid for all its cells
                            for row_offset in range(tower.height):
                                for col_offset in range(tower.width):
                                    cell = (mirrored_row + row_offset, mirrored_col + col_offset)
                                    if is_cell_in_bounds(cell, self.grid):
                                        self.occupancy_grid[cell] = mirrored_tower
                                        # mirror also the normal grid cell
                                        self.grid[cell[0]][cell[1]] = TOWER_P2
                            
                            self.unique_troops.add(mirrored_tower)
                            
                else:
                    # mirror other grid cells
                    self.grid[self.height-row-1][col] = self.grid[row][col]

    def world_generation(self):
        self.generate_river()
        self.generate_towers()
        self.generate_mock_bridges()
        self.mirror_arena()
    
    """utils"""
    def is_movable_cell(self, row, col, moving_troop=None):
        if not is_cell_in_bounds((row, col), self.grid):
            return False
        if not is_walkable(row, col, self.grid):
            return False
        if (row, col) in self.occupancy_grid and moving_troop != self.occupancy_grid[(row, col)]: # check if the cell is occupied by itself, this would mean it can move there
            return False
        return True
    
    def is_placable_cell(self, row, col, team, moving_troop=None):
        if not is_cell_in_bounds((row, col), self.grid):
            return False
        if not is_walkable(row, col, self.grid):
            return False
        if (row, col) in self.occupancy_grid and moving_troop != self.occupancy_grid[(row, col)]: # check if the cell is occupied by itself, this would mean it can move there
            return False
        if team == 1 and row < self.height//2 + self.height_of_river: # first half of the arena
            return False
        if team == 2 and row > self.height//2 - self.height_of_river: # second half of the arena
            return False
        
        return True

    def spawn_unit(self, troop, cell: (int, int)):
        if not is_cell_in_bounds(cell, self.grid):
            return False

        #scaled_width = max(1, int(self.width/18*troop.width//2))
        #scaled_height = max(1, int(self.height/32*troop.height//2))
    
        #troop.width = scaled_width
        #troop.height = scaled_height

        # so we set the location to the top left corner of the troop and arena in it 
        troop.location = cell
        troop.arena = self

        occupied_cells = troop.occupied_cells({})
        # checking if all the other cells are valid   

        for occupied_cell in occupied_cells:
            if not self.is_placable_cell(occupied_cell[0], occupied_cell[1], troop.team, moving_troop=troop):
                return False
        
        for occupied_cell in occupied_cells:
            self.occupancy_grid[occupied_cell] = troop # we set the troop in all the cells it occupies
        
        self.unique_troops.add(troop)
        return True
    
    def move_unit(self, troop, new_cell: (int, int)):
        """
        Used to move a troop from old cell in the occupancy_grid
        """
        if not is_cell_in_bounds(new_cell, self.grid):
            return False
        
        old_location = troop.location # we save the old location to move it back later
        troop.location = new_cell  # temporarily set to calculate occupied cells
        new_occupied_cells = troop.occupied_cells({})
        troop.location = old_location  # we move it back to the old location
        
        for cell in new_occupied_cells:
            if not self.is_movable_cell(cell[0], cell[1], moving_troop=troop):
                return False
        
        old_occupied_cells = troop.occupied_cells({})

        for cell in old_occupied_cells:
            if cell in self.occupancy_grid and self.occupancy_grid[cell] == troop: # kind of unecessary double check but better be safe
                self.occupancy_grid.pop(cell)

        troop.location = new_cell # to the new left top corner

        for cell in new_occupied_cells:
            self.occupancy_grid[cell] = troop # we set the troop in all the cells it occupies
        
    
        return True

    def remove_unit(self, troop):
        """
        Remove a troop from the occupancy grid (clean up all cells it occupies).
        """
        self.unique_troops.remove(troop)
        occupied_cells = troop.occupied_cells({})  # Pass empty dict
        for cell in occupied_cells:
            if cell in self.occupancy_grid and self.occupancy_grid[cell] == troop:
                self.occupancy_grid.pop(cell)
        return True

if __name__ == "__main__":
    arena = Arena(1600) 
    arena.world_generation()
