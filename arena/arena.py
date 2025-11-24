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
        self.towers_P1 = {} # dict key: tower_n value: tower_obj
        self.towers_P2 = {}


        """POST GENERATION"""
        self.occupancy_grid = {} # dictionary of cells and ids of the troop inside of them (max one per cell) --> key: (row, col) value: id
        self.unique_troops = set()
        self.frame_count = 0

        self.asset_manager = None
        self.arena_background_dirty = True

        self.one_minute = TICKS_PER_SECOND*60
        self.time_left = self.one_minute*3 # the match is supposed to be 3 minutes

        self.elixir_multiplier = 1.0

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
        troop_health, troop_damage, troop_movement_speed, troop_attack_type, troop_attack_speed, troop_attack_range, troop_attack_aggro_range, troop_attack_cooldown, troop_width, troop_height, troop_type, troop_favorite_target = extract_tower_stats(tower_type)
        
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
            asset_manager=self.asset_manager,
            troop_type=troop_type,
            troop_favorite_target=troop_favorite_target
        )
        if tower_type == 0: # deactivate the middle tower 
            tower.is_active = False

        self.unique_troops.add(tower)
        if team == 1:
            self.towers_P1[tower_type] = tower
        else:
            self.towers_P2[tower_type] = tower

        for index_row in range(bottom_left[1]-scaled_height+1, bottom_left[1]+1):
            for index_col in range(bottom_left[0], bottom_left[0]+scaled_width):
        
                self.grid[index_row][index_col] = tower_grid_type + tower_type
        
                rel_row = index_row - top_left[0]  # relative to top-left
                rel_col = index_col - top_left[1]

                if (rel_row == 0 or rel_row == tower.height - 1 or rel_col == 0 or rel_col == tower.width - 1) and (rel_col % GAP_BETWEEN_TOWER_CELLS == 0 or rel_row % GAP_BETWEEN_TOWER_CELLS == 0):
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

    def generate_mock_bridges(self, bridge_width=1):
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
    
    def mirror_arena(self, team=2):
        lower_center = self.height//2 
        print("lower center", lower_center)

        # Find all team 1 towers from unique_troops (more reliable than scanning grid)
        for tower in list(self.unique_troops):
            if tower.is_tower and tower.team == 1:
                # extract tower type from name
                result = re.search(r'Tower\s*(-?\d+)', tower.name)
                if result:
                    tower_type = int(result.group(1))
                    
                    # calculate mirrored position
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
                        attack_range=int(tower.attack_range/MULTIPLIER_GRID_HEIGHT),
                        attack_aggro_range=int(tower.attack_aggro_range/MULTIPLIER_GRID_HEIGHT),
                        attack_cooldown=tower.attack_cooldown,
                        width=tower.width,  
                        height=tower.height, 
                        color=(255, 0, 0),
                        team=team,
                        location=(mirrored_row, mirrored_col),
                        arena=self,
                        asset_manager=self.asset_manager,
                        troop_type=tower.troop_type,
                        troop_favorite_target=tower.troop_favorite_target
                    )
                    if tower_type == 0:
                        mirrored_tower.is_active = False
                    
                    # Cache cells and place in grid
                    mirrored_tower.cached_cells = []
                    
                    for row_offset in range(tower.height):
                        for col_offset in range(tower.width):
                            cell = (mirrored_row + row_offset, mirrored_col + col_offset)
                            if is_cell_in_bounds(cell, self.grid):
                                self.grid[cell[0]][cell[1]] = TOWER_P2 + tower_type
                                mirrored_tower.cached_cells.append(cell)
                                
                                # Store only border cells in occupancy_grid
                                if (row_offset == 0 or row_offset == tower.height - 1 or col_offset == 0 or col_offset == tower.width - 1) and (col_offset % 2 == 0 or row_offset % 2 == 0):
                                    self.occupancy_grid[cell] = mirrored_tower
                    
                    self.unique_troops.add(mirrored_tower)
                    if team == 1:
                        self.towers_P1[tower_type] = mirrored_tower
                    else:
                        self.towers_P2[tower_type] = mirrored_tower
        
        # Mirror non-tower grid cells
        for row in range(lower_center, self.height):
            for col in range(self.width):
                if self.grid[row][col] not in [TOWER_P1, TOWER_P2, TOWER_P1+1, TOWER_P2+1, TOWER_P1-1, TOWER_P2-1]:
                    self.grid[self.height-row-1][col] = self.grid[row][col]

    def world_generation(self):
        self.generate_river()
        self.generate_towers()
        self.generate_mock_bridges()
        self.mirror_arena()
    
    """utils""" 
    def tick(self):
        self.frame_count += 1
        self.time_left -= 1
        if self.time_left == self.one_minute:
            print("1 minute left")
            self.elixir_multiplier = 2.0 # we double the elixir in the last minute
        if self.time_left <= 0:
            print("Match over")
            return False

        return True


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
        occupied_cells = troop.occupied_cells({})
        for cell in occupied_cells:
            if cell in self.occupancy_grid and self.occupancy_grid[cell] == troop:
                self.occupancy_grid.pop(cell)
        return True
    
    def remove_tower(self, tower_troop):
        """
        Remove a tower from the occupancy grid (clean up all cells it occupies).
        """
        for troop in self.unique_troops:
            if troop.name.startswith("Tower"):
                if troop.team == tower_troop.team and troop.is_active == False and troop.is_alive:
                    troop.is_active = True
                    if troop.team == 1: #TODO: check if this is correct
                        self.central_tower_P1_active = True
                    else: 
                        self.central_tower_P2_active = True

        self.unique_troops.discard(tower_troop)
        occupied_cells = tower_troop.occupied_cells({})
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
        return True

if __name__ == "__main__":
    arena = Arena(1600) 
    arena.world_generation()
