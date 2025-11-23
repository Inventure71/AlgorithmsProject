from math import inf
import os
import random
import pygame
from constants import *
from arena.utils.random_utils import is_cell_in_bounds, is_in_attack_range, calculate_center_to_center_distance
from arena.utils.find_path_bfs import find_path_bfs

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
        asset_manager = None,
        ):
        self.name = name
        self.health = health
        self.max_health = health
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
        self.is_active = True
        self.is_targetting_something = None # Value should be of value Troop, this should be changed when the troop starts attacking something so that it stops moving and doesn't focus on something else
        self.is_tower = self.name.startswith("Tower") # check if this is a tower (towers need grid cleanup)

        """EXP"""
        self.target = None
        self.in_process_attack = False
        
        """ASSET MANAGER"""
        self.asset_manager = asset_manager
        # open pygame surface for the sprite
        self.sprite = self._load_sprite()
    
    """HELPER FUNCTIONS"""
    def find_closest_target(self, start_location, occupancy_grid, got_blocked=False):
        # by default troops attack the tower, so we don't need to check if the distance from the tower is in range

        minimum_distance_to_troop, closest_troop = self.find_closest_enemy_troop(start_location, occupancy_grid)
        # path to the tower (we ignore troops here)
        if got_blocked: # means we got blocked by a troop so we need to path considering the troops
            path = find_path_bfs(self.location, self.arena.grid, occupancy_grid, self, cell_type=self.tower_type)
        else: # lighter pathing, we ignore troops
            path = find_path_bfs(self.location, self.arena.grid, {}, self, cell_type=self.tower_type)
        
        if self.attack_aggro_range >= minimum_distance_to_troop >= 0:
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
        
        checked_troops = set()
        
        for cell in occupancy_grid: # we could use arena.unique_troops instead of occupancy_grid
            troop = occupancy_grid[cell]
            # skip if already checked, same team, or dead
            if troop in checked_troops or troop.team == self.team or not troop.is_alive:
                continue
            
            checked_troops.add(troop)
            
            # using center-to-center distance for consistency
            distance = calculate_center_to_center_distance(self, troop)
            
            if distance < minimum_distance:
                minimum_distance = distance
                closest_troop = troop
        
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
        """Get a scaled sprite, using asset manager cache."""
        if self.asset_manager:
            return self.asset_manager.get_scaled_sprite(self.sprite, visual_width, visual_height)
        else:
            # Fallback if no asset manager provided
            sprite_width, sprite_height = self.sprite.get_size()
            scale_x = visual_width / sprite_width
            scale_y = visual_height / sprite_height
            scale = min(scale_x, scale_y)
            scaled_width = int(sprite_width * scale)
            scaled_height = int(sprite_height * scale)
            return pygame.transform.scale(self.sprite, (scaled_width, scaled_height))
    
    def _load_sprite(self):
        """Load a sprite image for this troop using asset manager."""
        if self.asset_manager:
            return self.asset_manager.get_troop_sprite(self.name, self.team)
        else:
            # Fallback: create colored surface
            surface = pygame.Surface((self.width, self.height))
            surface.fill(self.color)
            return surface

    """MAIN FUNCTIONS"""
    def move_to_tower(self, got_blocked=False, steps_done=0):
        
        path = None

        if not self.is_targetting_something:
            # we first check if something can be targetted
            # let's see if we can attack something near us
            path = self.find_closest_target(self.location, self.arena.occupancy_grid, got_blocked=got_blocked) # this will return the path to the option we are going for 

        if self.is_targetting_something: # if we are now targetting something we do this instead of moving torward the towers
            if not self.is_targetting_something.is_alive:
                self.is_targetting_something = None
                path = self.find_closest_target(self.location, self.arena.occupancy_grid)
        
            else:
                # we overwrite the path to the tower to the one to the troop
                # if it is still alive then
                # make sure that the troop is still in range of the troop that it is attacking if not walk there
                if not is_in_attack_range(self, self.is_targetting_something):
                    print(f"{self.name} not in range, finding path to troop")
                    path = find_path_bfs(self.location, self.arena.grid, self.arena.occupancy_grid, self, cell_type=self.is_targetting_something) #TODO: make sure this is actually able to follow a troop
                    print(f"{self.name} trying to path to {self.is_targetting_something.name}", path)
                else:
                    if self.movement_speed != 0:
                        print(f"{self.name} already in range, no need to move, Attacking")
                    path = None
                    self.attack()
    
        if not path:
            #print("reached objective")
            return

        # Line 172-180 - replace with:
        # Calculate how many steps needed
        # Path includes start position, so actual steps = len(path) - 1
        # We want to stop when within attack_range of target
        step_to_do = self.movement_speed - steps_done
        steps_done = 0

        if step_to_do <= 0:
            #print("already in range, no need to move")
            return
        else:
            print(f"{self.name} in theory wants to move {step_to_do} steps")
            self.in_process_attack = None # reset the attack in process flag

        while steps_done < step_to_do:
            # start from index 1 not 0 so we avoid the same cell 
            steps_done = steps_done + 1 

            if steps_done >= len(path):
                print("path not long enough")
                return 
            
            if is_in_attack_range(self, self.is_targetting_something):
                print(f"{self.name} is in attack range of {self.is_targetting_something.name}, no need to move, attacking")
                self.attack()
                return
            
            if not self.arena.move_unit(self, path[steps_done]):
                print("Unit in the way checking again path considering troops")  
                
                self.move_to_tower(got_blocked=True, steps_done=steps_done - 1)
                return

            else:
                print(f"{self.name} moves to {path[steps_done]}")
                self.location = path[steps_done]
    
    def attack(self):
        if self.is_alive and self.is_active:
            if self.in_process_attack:
                if (self.arena.frame_count-self.in_process_attack) % self.attack_speed == 0:
                    self.is_targetting_something.take_damage(self.damage, source_troop=self)
                    
            else:
                self.in_process_attack = self.arena.frame_count

            return True
        print(f"{self.name} is dead or inactive, cannot attack")
        return False

    def take_damage(self, damage, source_troop=None):
        if self.health - damage <= 0:
            self.is_alive = False
            if self.is_tower:
                self.arena.remove_tower(self) # tower has a different cleanup function
            else:
                self.arena.remove_unit(self)
        else:
            self.health -= damage
            print(f"{self.name} of team {self.team} takes {damage} damage from {source_troop.name} of team {source_troop.team}, {self.health} health left")

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

        