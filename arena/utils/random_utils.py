import math
from constants import *
from deck.stats import *

"""
Why we don't use center-to-center distance and we use edge-to-edge distance:
- Range is measured between hitboxes, not between center points
- A big troop and a small troop are treated fairly (es towers)
- If their borders are exactly attack_range apart, the attack is allowed
- This matches the visual expectation: “As soon as my troop’s attack circle touches the enemy’s hitbox, it can attack.”

"""

def is_in_attack_range(source_troop, target_troop):
    """
    Checks if target is within attack range using edge-to-edge distance

    - Time: Worst case = Average case = O(1)
    - Space: O(1)
    """
    if not target_troop or not target_troop.is_alive:
        return False
    # use edge-to-edge distance to match visual representation test also the borders one
    dist = calculate_edge_to_edge_distance(source_troop, target_troop)

    if dist <= source_troop.attack_range:
        #print(f"{source_troop.name} is in attack range of {target_troop.name} at distance {dist}")
        return True
    else:
        #print(f"{source_troop.name} is not in attack range of {target_troop.name} at distance {dist}")
        return False

def calculate_edge_to_edge_distance(source_troop, target_troop):
    """
    Calculate the shortest distance between the borders of two rectangular troops
    Returns 0 if they overlap

    - Time: Worst case = Average case = O(1)
    - Space: O(1)
    """
    # get bounding boxes:
    # source_troop: (row, col) is top-left corner
    source_min_row = source_troop.location[0]
    source_max_row = source_troop.location[0] + source_troop.height - 1
    source_min_col = source_troop.location[1]
    source_max_col = source_troop.location[1] + source_troop.width - 1
    
    target_min_row = target_troop.location[0]
    target_max_row = target_troop.location[0] + target_troop.height - 1
    target_min_col = target_troop.location[1]
    target_max_col = target_troop.location[1] + target_troop.width - 1
    
    # check if rectangles overlap
    if (source_max_row >= target_min_row and source_min_row <= target_max_row and
        source_max_col >= target_min_col and source_min_col <= target_max_col):
        return 0.0  # they overlap
    
    # calculate closest points on each rectangle
    # for source rectangle, find closest point to target
    closest_source_row = max(source_min_row, min(target_min_row + target_troop.height / 2.0, source_max_row))
    closest_source_col = max(source_min_col, min(target_min_col + target_troop.width / 2.0, source_max_col))
    
    # for target rectangle, find closest point to source
    closest_target_row = max(target_min_row, min(source_min_row + source_troop.height / 2.0, target_max_row))
    closest_target_col = max(target_min_col, min(source_min_col + source_troop.width / 2.0, target_max_col))
    
    # calculate euclidean distance between closest points
    distance = math.sqrt(
        (closest_target_row - closest_source_row)**2 + 
        (closest_target_col - closest_source_col)**2
    )
    
    return distance

def is_walkable(row, col, grid, is_flying=False):
    """
    Checks if a cell is walkable based on terrain type and flying ability

    - Time: Worst case = Average case = O(1) grid lookup and set membership check are constant time
    - Space: O(1)
    """
    if is_flying:
        return grid[row][col] in flyable_cells
    else:
        return grid[row][col] in walkable_cells

def is_cell_in_bounds(cell: (int, int), grid):
    """
    Checks if a cell coordinate is within grid boundaries

    - Time: Worst case = Average case = O(1)
    - Space: O(1)
    """
    if not (cell[0] >= 0 and cell[0] < len(grid)):
        return False

    if not (cell[1] >= 0 and cell[1] < len(grid[0])):
        return False

    return True

def extract_tower_stats(tower_type):
    """
    Extracts tower statistics from predefined stat dictionaries

    - Time: Worst case = Average case = O(1)
    - Space: O(1)
    """
    if tower_type in (1, -1): # we check if it is a left or right tower
        tower_stats = stats_tower_small # we select the small tower stats
    else:
        tower_stats = stats_tower_center # we select the center tower stats

    troop_health = tower_stats.get("troop_health")
    troop_damage = tower_stats.get("troop_damage")
    troop_movement_speed = tower_stats.get("troop_movement_speed")
    troop_attack_type = tower_stats.get("troop_attack_type")
    troop_attack_speed = tower_stats.get("troop_attack_speed")
    troop_attack_range = tower_stats.get("troop_attack_range")
    troop_attack_aggro_range = troop_attack_range # this is done on purpose to avoid possible confusion, for towers the aggro range is the same as the attack range
    troop_attack_tile_radius = tower_stats.get("troop_attack_tile_radius")
    troop_width = tower_stats.get("troop_width")
    troop_height = tower_stats.get("troop_height")
    troop_type = tower_stats.get("troop_type")
    troop_favorite_target = tower_stats.get("troop_favorite_target")
    troop_can_target_air = tower_stats.get("troop_can_target_air")

    return (
        troop_health,
        troop_damage,
        troop_movement_speed,
        troop_attack_type,
        troop_attack_speed,
        troop_attack_range,
        troop_attack_aggro_range,
        troop_attack_tile_radius,
        troop_width,
        troop_height,
        troop_type,
        troop_favorite_target,
        troop_can_target_air,
    )

