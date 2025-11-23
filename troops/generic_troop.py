from math import inf
import os
import random

import pygame
from constants import *
from arena.utils.random_utils import calculate_distance, is_cell_in_bounds
from arena.utils.find_path_bfs import find_path_bfs

# sprite cache to avoid repeated file I/O
_sprite_cache = {}
_scaled_sprite_cache = {}

class Troop:
    def __init__(
        self,
        name,
        health,
        damage,
        movement_speed,
        attack_type,
        attack_speed,
        attack_range,
        attack_aggro_range,
        attack_cooldown,
        width,
        height,
        color,
        team,
        location = None,
        arena = None,
        ):
        self.name = name
        self.health = health
        self.damage = damage
        self.movement_speed = int(movement_speed * MULTIPLIER_GRID_HEIGHT)
        self.attack_speed = attack_speed
        self.attack_range = int(attack_range * MULTIPLIER_GRID_HEIGHT)
        self.attack_aggro_range = int(attack_aggro_range * MULTIPLIER_GRID_HEIGHT) # we use this to check if we are in range to get triggered by something
        self.attack_cooldown = attack_cooldown
        self.team = team
        self.width = width
        self.height = height

        self.tower_type = TOWER_P2 if self.team == 1 else TOWER_P1

        self.location = location # (row, col)
        self.arena = arena

        self.color = color

        self.is_alive = True
        self.is_targetting_something = None # Value should be of value Troop, this should be changed when the troop starts attacking something so that it stops moving and doesn't focus on something else
        # open pygame surface for the sprite
        self.sprite = self._load_sprite()

        """EXP"""
        self.target = None
    
    """HELPER FUNCTIONS"""
    def find_closest_target(self, start_location, occupancy_grid):
        # by default troops attack the tower, so we don't need to check if the distance from the tower is in range

        minimum_distance_to_troop, closest_troop = self.find_closest_enemy_troop(start_location, occupancy_grid)
        # path to the tower (we ignore troops here)
        path = find_path_bfs(self.location, self.arena.grid, {}, self, cell_type=self.tower_type)
        if not path:
            distance_from_tower = inf
        else:
            distance_from_tower = len(path) # we can use len(path) how distant we are from the tower

        if self.attack_aggro_range >= minimum_distance_to_troop >= 0 and minimum_distance_to_troop < distance_from_tower:
            # select troop (this also includes the tower)
            self.is_targetting_something = closest_troop
            print("targetting troop", closest_troop.name)
            path = find_path_bfs(self.location, self.arena.grid, self.arena.occupancy_grid, self, cell_type=self.is_targetting_something) #TODO: make sure this is actually able to follow a troop

        else:
            # we select tower just for walking in that direction, no locking on it. 
            self.is_targetting_something = None
                    
        return path 

    def find_closest_enemy_troop(self, location, occupancy_grid): # this should only be run if no target is active.
        closest_troop = None
        minimum_distance = inf
        for cell in occupancy_grid: # each cell contains a troop
            troop = occupancy_grid[cell]
            if troop.team != self.team and troop.is_alive: # only check for alive troops
                distance = calculate_distance(location, cell)
                if distance < minimum_distance:
                    minimum_distance = distance
                    closest_troop = troop

        #print("closest troop", closest_troop.name if closest_troop else "none", "at distance", minimum_distance)
        return minimum_distance, closest_troop

    def occupied_cells(self, occupancy_grid={}):
        if self.location is None or self.arena is None:
            raise ValueError("Location and arena must be set before calling occupied_cells")

        base_row, base_col = self.location # (top left corner)
        for row in range(base_row, base_row + self.height):
            for col in range(base_col, base_col + self.width):
                if is_cell_in_bounds((row, col), self.arena.grid):
                    occupancy_grid[(row, col)] = self
        
        return occupancy_grid

    """SPRITE LOADING"""
    def get_scaled_sprite(self, visual_width, visual_height):
        """Get a scaled sprite, using cache to avoid repeated scaling operations"""
        # Calculate the target scaled size
        sprite_width, sprite_height = self.sprite.get_size()
        scale_x = visual_width / sprite_width
        scale_y = visual_height / sprite_height
        scale = min(scale_x, scale_y)  # Use smaller scale to fit within bounds
        
        scaled_width = int(sprite_width * scale)
        scaled_height = int(sprite_height * scale)
        
        # Create cache key
        cache_key = (id(self.sprite), scaled_width, scaled_height)
        
        if cache_key in _scaled_sprite_cache:
            return _scaled_sprite_cache[cache_key]
        
        # Scale and cache
        scaled_sprite = pygame.transform.scale(self.sprite, (scaled_width, scaled_height))
        _scaled_sprite_cache[cache_key] = scaled_sprite
        return scaled_sprite
    
    def _load_sprite(self):
        """Load a sprite image for this troop, using cache to avoid repeated file I/O"""
        # Check cache first
        cache_key = (self.name, self.team)
        if cache_key in _sprite_cache:
            return _sprite_cache[cache_key]
        
        # Map troop name to asset folder name (match exact case)
        troop_folder_map = {
            "barbarian": "barbarian",
            "archer": "Archer"  # Note: capital A to match folder name
        }
        
        troop_folder = troop_folder_map.get(self.name, None)
        if not troop_folder:
            # Fallback to colored surface if troop not found
            surface = pygame.Surface((self.width, self.height))
            surface.fill(self.color)
            _sprite_cache[cache_key] = surface
            return surface
        
        # Build path to sprite file
        team_folder = f"Team {self.team}"
        sprite_path = os.path.join("assets", "usable_assets", troop_folder, team_folder)
        
        if not os.path.exists(sprite_path):
            # Fallback to colored surface if path doesn't exist
            surface = pygame.Surface((self.width, self.height))
            surface.fill(self.color)
            _sprite_cache[cache_key] = surface
            return surface
        
        # Get first PNG file in the directory (or you can specify a specific one)
        sprite_files = [f for f in os.listdir(sprite_path) if f.endswith('.png')]
        if not sprite_files:
            # Fallback to colored surface if no sprites found
            surface = pygame.Surface((self.width, self.height))
            surface.fill(self.color)
            _sprite_cache[cache_key] = surface
            return surface
        
        # Load the first sprite (or you can pick a specific one)
        sprite_file = os.path.join(sprite_path, sorted(sprite_files)[0])
        try:
            sprite = pygame.image.load(sprite_file).convert_alpha()
            _sprite_cache[cache_key] = sprite
            return sprite
        except Exception as e:
            print(f"Error loading sprite {sprite_file}: {e}")
            # Fallback to colored surface
            surface = pygame.Surface((self.width, self.height))
            surface.fill(self.color)
            _sprite_cache[cache_key] = surface
            return surface
            
    """MAIN FUNCTIONS"""
    def move_to_tower(self):
        if self.movement_speed == 0:
            # for example if we have the tower as a troop it wouldn't move
            return 
        
        path = None

        if not self.is_targetting_something:
            # we first check if something can be targetted
            # let's see if we can attack something near us
            path = self.find_closest_target(self.location, self.arena.occupancy_grid) # this will return the path to the option we are going for 

        if self.is_targetting_something: # if we are now targetting something we do this instead of moving torward the towers
            if not self.is_targetting_something.is_alive:
                self.is_targetting_something = None
                path = self.find_closest_target(self.location, self.arena.occupancy_grid)
        
            else:
                # we overwrite the path to the tower to the one to the troop
                # if it is still alive then
                # make sure that the troop is still in range of the troop that it is attacking if not walk there
                if calculate_distance(self.location, self.is_targetting_something.location) > self.attack_range:
                    print(f"{self.name} not in range, finding path to troop")
                    path = find_path_bfs(self.location, self.arena.grid, self.arena.occupancy_grid, self, cell_type=self.is_targetting_something) #TODO: make sure this is actually able to follow a troop
                    print("path", path)
                else:
                    print(f"{self.name} already in range, no need to move")
                    path = None
        
        moves_this_tick_to_do = self.movement_speed # 1
        moves_this_tick_done = 0
        
        if path:
            distance_to_target = len(path)
            moves_this_tick_to_do = min(distance_to_target - self.attack_range, self.movement_speed)
        else:
            print("no path found")
            return

        while moves_this_tick_done < moves_this_tick_to_do:
            # start from index 1 not 0 so we avoid the same cell 
            next_index = moves_this_tick_done + 1
            if not path or next_index >= len(path):
                print("reached end of path")
                break
        
            if len(path[next_index::]) <= self.attack_range:
                path = None
                print("already in range, no need to move")
                break
            else:
                print(len(path), self.attack_range)
            
            
            if not self.arena.move_unit(self, path[moves_this_tick_done + 1]):
                print("Unit in the way checking again path considering troops")
                path = find_path_bfs(self.location, self.arena.grid, self.arena.occupancy_grid, self, cell_type=self.tower_type)
                moves_this_tick_to_do = moves_this_tick_to_do - moves_this_tick_done
                moves_this_tick_done = 0
                continue
            else:
                self.location = path[moves_this_tick_done + 1]
                moves_this_tick_done += 1
    
    def attack(self, target):
        pass

    def take_damage(self, damage):
        if self.health - damage <= 0:
            self.is_alive = False
        else:
            self.health -= damage

    """REMOVABLE"""          
    def move_random_target(self):
        if  not self.target or self.location == self.target:
            self.target = (random.randint(0, self.arena.height-1), random.randint(0, self.arena.width-1))
        
        path = find_path_bfs(self.location, self.arena.grid, self.arena.occupancy_grid, self, goal_cell=self.target)
        
        if path:
            for path_index in range(1, self.movement_speed + 1):
                if path_index < len(path):
                    if not self.arena.move_unit(self, path[path_index]):
                        print("ERROR MOVING")
                        self.target = (random.randint(0, self.arena.height-1), random.randint(0, self.arena.width-1))
                    else:
                        self.location = path[path_index]
                        
                    
        else:
            print("NO PATH FOUND")
            self.target = (random.randint(0, self.arena.height-1), random.randint(0, self.arena.width-1))

        