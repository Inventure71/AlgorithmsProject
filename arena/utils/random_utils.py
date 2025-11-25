import re
from tkinter import N
from constants import *
import math
from deck.stats import *

def is_in_attack_range(source_troop, target_troop):
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

def calculate_distance(current_cell=None, target_cell=None, target_troop=None, current_troop=None):
    shortest_distance = math.inf
    if current_cell and target_cell:
        return math.sqrt((target_cell[0]-current_cell[0])**2+(target_cell[1]-current_cell[1])**2)
    elif current_troop and target_troop:
        for cell in list(current_troop.occupied_cells().keys()):
            for target_cell in list(target_troop.occupied_cells().keys()):
                distance = math.sqrt((target_cell[0]-cell[0])**2+(target_cell[1]-cell[1])**2)
                if distance < shortest_distance:
                    shortest_distance = distance
        return shortest_distance
    return math.inf

def calculate_center_to_center_distance(current_troop, target_troop):
    """Calculate distance from center of current_troop to center of target_troop"""
    # Calculate center of current troop
    current_center_row = current_troop.location[0] + current_troop.height / 2.0
    current_center_col = current_troop.location[1] + current_troop.width / 2.0
    
    # Calculate center of target troop
    target_center_row = target_troop.location[0] + target_troop.height / 2.0
    target_center_col = target_troop.location[1] + target_troop.width / 2.0
    
    # Euclidean distance between centers
    distance = math.sqrt(
        (target_center_row - current_center_row)**2 + 
        (target_center_col - current_center_col)**2
    )

    return distance

def calculate_edge_to_edge_distance(source_troop, target_troop):
    """
    Calculate the shortest distance between the borders of two rectangular troops.
    Returns 0 if they overlap.
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
    if is_flying:
        return grid[row][col] in flyable_cells
    else:
        return grid[row][col] in walkable_cells

def is_cell_in_bounds(cell: (int, int), grid):
    if not (cell[0] >= 0 and cell[0] < len(grid)):
        return False

    if not (cell[1] >= 0 and cell[1] < len(grid[0])):
        return False

    return True

def extract_tower_stats(tower_type):
    if tower_type == 1 or tower_type == -1:
        troop_health = stats_tower_small.get("troop_health")
        troop_damage = stats_tower_small.get("troop_damage")
        troop_movement_speed = stats_tower_small.get("troop_movement_speed")
        troop_attack_type = stats_tower_small.get("troop_attack_type")
        troop_attack_speed = stats_tower_small.get("troop_attack_speed")
        troop_attack_range = stats_tower_small.get("troop_attack_range")
        troop_attack_aggro_range = stats_tower_small.get("troop_attack_range")
        troop_attack_cooldown = stats_tower_small.get("troop_attack_cooldown")
        troop_attack_tile_radius = stats_tower_small.get("troop_attack_tile_radius")
        troop_width = stats_tower_small.get("troop_width")
        troop_height = stats_tower_small.get("troop_height")
        troop_type = stats_tower_small.get("troop_type")
        troop_favorite_target = stats_tower_small.get("troop_favorite_target")
        troop_can_target_air = stats_tower_small.get("troop_can_target_air")
        return troop_health, troop_damage, troop_movement_speed, troop_attack_type, troop_attack_speed, troop_attack_range, troop_attack_aggro_range, troop_attack_cooldown, troop_attack_tile_radius, troop_width, troop_height, troop_type, troop_favorite_target, troop_can_target_air
    else:
        troop_health = stats_tower_center.get("troop_health")
        troop_damage = stats_tower_center.get("troop_damage")
        troop_movement_speed = stats_tower_center.get("troop_movement_speed")
        troop_attack_type = stats_tower_center.get("troop_attack_type")
        troop_attack_speed = stats_tower_center.get("troop_attack_speed")
        troop_attack_range = stats_tower_center.get("troop_attack_range")
        troop_attack_aggro_range = stats_tower_center.get("troop_attack_range")
        troop_attack_cooldown = stats_tower_center.get("troop_attack_cooldown")
        troop_attack_tile_radius = stats_tower_center.get("troop_attack_tile_radius")
        troop_width = stats_tower_center.get("troop_width")
        troop_height = stats_tower_center.get("troop_height")
        troop_type = stats_tower_center.get("troop_type")
        troop_favorite_target = stats_tower_center.get("troop_favorite_target")
        troop_can_target_air = stats_tower_center.get("troop_can_target_air")
        return  troop_health, troop_damage, troop_movement_speed, troop_attack_type, troop_attack_speed, troop_attack_range, troop_attack_aggro_range, troop_attack_cooldown, troop_attack_tile_radius, troop_width, troop_height, troop_type, troop_favorite_target, troop_can_target_air
