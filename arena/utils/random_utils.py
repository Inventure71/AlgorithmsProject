import re
from constants import *
import math
from deck.stats import *

def calculate_distance(current_cell, target_cell):
    return math.sqrt((target_cell[0]-current_cell[0])**2+(target_cell[1]-current_cell[1])**2)

def is_walkable(row, col, grid):
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
        troop_attack_cooldown = stats_tower_small.get("troop_attack_cooldown")
        troop_width = stats_tower_small.get("troop_width")
        troop_height = stats_tower_small.get("troop_height")
        return troop_health, troop_damage, troop_movement_speed, troop_attack_type, troop_attack_speed, troop_attack_range, troop_attack_cooldown, troop_width, troop_height
    else:
        troop_health = stats_tower_center.get("troop_health")
        troop_damage = stats_tower_center.get("troop_damage")
        troop_movement_speed = stats_tower_center.get("troop_movement_speed")
        troop_attack_type = stats_tower_center.get("troop_attack_type")
        troop_attack_speed = stats_tower_center.get("troop_attack_speed")
        troop_attack_range = stats_tower_center.get("troop_attack_range")
        troop_attack_cooldown = stats_tower_center.get("troop_attack_cooldown")
        troop_width = stats_tower_center.get("troop_width")
        troop_height = stats_tower_center.get("troop_height")
        return troop_health, troop_damage, troop_movement_speed, troop_attack_type, troop_attack_speed, troop_attack_range, troop_attack_cooldown, troop_width, troop_height