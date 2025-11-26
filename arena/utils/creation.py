import re
from constants import *
from troops.generic_troop import Troop
from arena.utils.random_utils import is_cell_in_bounds, extract_tower_stats

def generate_river(height, height_of_river, arena):
    # center is always going to be in the middle of an even number of cells, but there isn't a precise one so we handle both 
    # first center found is lower center (between the two even)

    # remember higher center is lower center + 1 
    # so we have two systems that go from lower center - (height_of_river//2) to lower center + (height_of_river//2) and from lower center + 1 - (height_of_river//2) to lower center + 1 + (height_of_river//2)
    # we combine them into one loop
    lower_center = height//2
    for i in range(lower_center, (lower_center)+(height_of_river - 1) + 1): #  lower_center-(int(self.height_of_river//2) - 1), (lower_center+1)+(int(self.height_of_river//2) - 1) + 1)
        #print("lower center", i)
        for index in range(len(arena.grid[i])):
            arena.grid[i][index] = WATER
    
    return True
        
def generate_tower(
    width,
    height,
    arena,
    asset_manager,
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
    troop_health, troop_damage, troop_movement_speed, troop_attack_type, troop_attack_speed, troop_attack_range, troop_attack_aggro_range, troop_attack_tile_radius, troop_width, troop_height, troop_type, troop_favorite_target, troop_can_target_air = extract_tower_stats(tower_type)
    
    # calculate scaled dimensions (these are the actual grid cell sizes)
    scaled_width = int(width/18*troop_width)
    scaled_height = int(height/32*troop_height)

    bottom_left = (int(width/18*distance_from_left), height-int(height/32*distance_from_bottom) - 1)
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
        attack_tile_radius=troop_attack_tile_radius,
        width=scaled_width,  
        height=scaled_height,  
        color="blue" if team == 1 else "red",
        team=team,
        location=top_left,
        arena=arena,
        asset_manager=asset_manager,
        troop_type=troop_type,
        troop_favorite_target=troop_favorite_target,
        troop_can_target_air=troop_can_target_air
    )
    if tower_type == 0: # deactivate the middle tower 
        tower.is_active = False

    arena.unique_troops.add(tower)
    if team == 1:
        arena.towers_P1[tower_type] = tower
    else:
        arena.towers_P2[tower_type] = tower

    for index_row in range(bottom_left[1]-scaled_height+1, bottom_left[1]+1):
        for index_col in range(bottom_left[0], bottom_left[0]+scaled_width):
    
            arena.grid[index_row][index_col] = tower_grid_type + tower_type
    
            rel_row = index_row - top_left[0]  # relative to top-left
            rel_col = index_col - top_left[1]

            if (rel_row == 0 or rel_row == tower.height - 1 or rel_col == 0 or rel_col == tower.width - 1) and (rel_col % GAP_BETWEEN_TOWER_CELLS == 0 or rel_row % GAP_BETWEEN_TOWER_CELLS == 0):
                arena.occupancy_grid[(index_row, index_col)] = tower
            
    return tower  # return the tower for potential use

def generate_mock_bridges(width, height, arena, height_of_river, bridge_width=1):
    """
    TODO: ONLY FOR DEBUGGING WE ARE GOING TO REMOVE THIS LATER AND MAKE IT GOOD
    """
    # scale bridge width to match arena size (similar to tower scaling)
    scaled_bridge_width = int(width/18 * bridge_width)
    scaled_bridge_width = max(1, scaled_bridge_width)  # ensure minimum width of 1
    
    # approximate x-centers of the princess towers (distance_from_left + half width)
    # left: 2 + 1.5 => 3.5/18 of width | right: 13 + 1.5 => 14.5/18 of width
    left_x  = int(width * (3.5 / 18.0))
    right_x = int(width * (14.5 / 18.0))

    lower_center = height // 2
    river_rows = range(lower_center, lower_center + height_of_river)
    half = scaled_bridge_width // 2

    for y in river_rows:
        for bx in (left_x, right_x):
            for x in range(bx - half, bx + half + 1):
                if 0 <= x < width:
                    # only overwrite river to make visible strips
                    if arena.grid[y][x] == 2:
                        arena.grid[y][x] = BRIDGE
    
    return True

def mirror_arena(height, width, arena, asset_manager, team=2):
    lower_center = height//2 
    print("lower center", lower_center)

    # find all team 1 towers from unique_troops (more reliable than scanning grid)
    for tower in list(arena.unique_troops):
        if tower.is_tower and tower.team == 1:
            # extract tower type from name
            result = re.search(r'Tower\s*(-?\d+)', tower.name)
            if result:
                tower_type = int(result.group(1))
                
                # calculate mirrored position
                orig_row, orig_col = tower.location
                mirrored_row = height - (orig_row + tower.height)
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
                    attack_tile_radius=tower.attack_tile_radius,
                    width=tower.width,  
                    height=tower.height, 
                    color=(255, 0, 0),
                    team=team,
                    location=(mirrored_row, mirrored_col),
                    arena=arena,
                    asset_manager=asset_manager,
                    troop_type=tower.troop_type,
                    troop_favorite_target=tower.troop_favorite_target,
                    troop_can_target_air=tower.troop_can_target_air
                )
                if tower_type == 0:
                    mirrored_tower.is_active = False
                                
                for row_offset in range(tower.height):
                    for col_offset in range(tower.width):
                        cell = (mirrored_row + row_offset, mirrored_col + col_offset)
                        if is_cell_in_bounds(cell, arena.grid):
                            arena.grid[cell[0]][cell[1]] = TOWER_P2 + tower_type
                            
                            # Store only border cells in occupancy_grid
                            if (row_offset == 0 or row_offset == tower.height - 1 or col_offset == 0 or col_offset == tower.width - 1) and (col_offset % 2 == 0 or row_offset % 2 == 0):
                                arena.occupancy_grid[cell] = mirrored_tower
                
                arena.unique_troops.add(mirrored_tower)
                if team == 1:
                    arena.towers_P1[tower_type] = mirrored_tower
                else:
                    arena.towers_P2[tower_type] = mirrored_tower
    
    # Mirror non-tower grid cells
    for row in range(lower_center, height):
        for col in range(width):
            if arena.grid[row][col] not in [TOWER_P1, TOWER_P2, TOWER_P1+1, TOWER_P2+1, TOWER_P1-1, TOWER_P2-1]:
                arena.grid[height-row-1][col] = arena.grid[row][col]
