from math import inf
from constants import *
from arena.utils.find_path_bfs import find_path_bfs
from arena.utils.random_utils import calculate_edge_to_edge_distance, is_cell_in_bounds, is_in_attack_range

class Troop:
    """
    Base class for all units in the game (troops and towers)
    """
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
        attack_tile_radius,
        width,
        height,
        color,
        team,
        location = (-1,-1), # this way the location will never be None
        arena = None,
        asset_manager = None,
        scale_multiplier = 1,
        troop_type = None,
        troop_favorite_target = "any",
        troop_can_target_air = False,
        troop_can_fly = False,
        ):
        self.name = name
        self.health = health
        self.max_health = health
        self.damage = damage
        self.attack_speed = attack_speed
        self.attack_range = int(attack_range * MULTIPLIER_GRID_HEIGHT)
        self.attack_aggro_range = int(attack_aggro_range * MULTIPLIER_GRID_HEIGHT) # we use this to check if we are in range to get triggered by something
        self.attack_tile_radius = int(attack_tile_radius * MULTIPLIER_GRID_HEIGHT) 

        self.troop_type = troop_type
        self.troop_favorite_target = troop_favorite_target
        self.troop_can_target_air = troop_can_target_air
        
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

        """TOWER"""
        self.is_tower = self.name.startswith("Tower") # check if this is a tower (towers need grid cleanup)
        
        self.tower_number = int(self.name.split(" ")[1]) if self.is_tower else None

        """EXP"""
        self.target = None
        self.in_process_attack = False
        
        """ASSET MANAGER"""
        self.asset_manager = asset_manager
        self.scale_multiplier = scale_multiplier
        self.sprite_number = 0 # 0 indexed for the sprite manager
        # open pygame surface for the sprite
        self.sprite = self.asset_manager.get_troop_sprite(self.name, self.team, self.sprite_number)

        """MOVEMENT"""
        self.troop_can_fly = troop_can_fly
        self.raw_movement_speed = (movement_speed * MULTIPLIER_GRID_HEIGHT / 2) # we divide by 2 just because the troops are a bit too fast, this can be fixed by changing the multiplier in the specs file but we feel like it is better to have more readable numbers there
        self.movement_accumulator = 0.0
        self.current_path = None
        self.current_path_index = 0
    
    """HELPER FUNCTIONS"""        
    def get_occupancy_grid(self):
        """
        Returns the appropriate occupancy grid dictionary for this troop type

        - Time: O(1) returns reference to existing dictionary
        - Space: O(1) no new allocation
        
        Note: A single 3D grid (grid[row][col][layer]) would add indexing overhead and complexity; two separate dicts are cleaner since ground and air units never collide
        """
        if self.troop_can_fly:
            return self.arena.occupancy_grid_flying
        else:
            return self.arena.occupancy_grid

    def reset_path(self):
        self.current_path = None
        self.current_path_index = 0
        #self.is_targetting_something = None
        
    def find_closest_target(self, got_blocked=False):
        """
        Finds the closest valid target and path to it
        
        - Time: O(n + BFS) where n is troop count for find_closest_enemy_troop and BFS is O(V + E) for pathfinding
        - Space: O(V) for BFS visited set and path
        
        Note: A priority queue would require O(n log n) updates every frame as troops move and distances change; linear O(n) scan is faster for fewer than 50 troops
        """
        # by default troops attack the tower, so we don't need to check if the distance from the tower is in range

        # we check if the troop is more than half to the right which means it would be in the right section and should need to check the right tower 
        if self.team == 1: # use the opposite team to find their towers
            towers = self.arena.towers_P2
        else:
            towers = self.arena.towers_P1

        if (self.arena.width // 2 - self.location[1]) < 0: 
            if len(towers) != 3 and 1 not in towers: # 1 is the right tower
                tower_number = 0
            else:
                # all towers still alive or the one we are targetting still there
                tower_number = 1

        else:
            if len(towers) != 3 and -1 not in towers: # -1 is the left tower
                tower_number = 0
            else:
                # all towers still alive or the one we are targetting still there
                tower_number = -1

        tower_to_find = self.tower_type + tower_number
        
        minimum_distance_to_troop, closest_troop = self.find_closest_enemy_troop()
        # path to the tower (we ignore troops here) or we use the current path if it is set
        if got_blocked: # means we got blocked by a troop so we need to path considering the troops
            path = find_path_bfs(self.location, self.arena.grid, self.get_occupancy_grid(), {}, self, cell_type=tower_to_find)
            self.current_path_index = 0
            if not path:
                print(f"{self.name} got blocked by a troop, no path found")

        elif self.current_path:
            path = self.current_path

        else: # lighter pathing, we ignore troops
            path = find_path_bfs(self.location, self.arena.grid, {}, {}, self, cell_type=tower_to_find)
            self.current_path_index = 0
        
        if self.attack_aggro_range >= minimum_distance_to_troop >= 0 and closest_troop is not None:
            should_lock_on = True # by default we lock on the troop
            
            # troops should not lock on the towers using the aggro range, they use the actual attack range, if something else is in the aggro range before that then they attack that troop not the tower
            if closest_troop.is_tower:
                if self.attack_range < minimum_distance_to_troop:
                    should_lock_on = False  # tower is in aggro range but not attack range
            
            if should_lock_on:
                # select troop (this also includes the tower)
                self.is_targetting_something = closest_troop
                #print("targetting troop", closest_troop.name)

                target_grid = closest_troop.get_occupancy_grid()
                collision_grid = self.get_occupancy_grid()

                path = find_path_bfs(self.location, self.arena.grid, collision_grid, target_grid, self, cell_type=self.is_targetting_something)
                self.current_path_index = 0
            else:
                # tower is in aggro range but not attack range, we walk toward it without locking on it
                self.is_targetting_something = None

        else:
            # we select tower just for walking in that direction, no locking on it. 
            self.is_targetting_something = None
        
        self.current_path = path
        return path 

    def find_closest_enemy_troop(self): # this should only be run if no target is active.
        """
        Finds the closest enemy troop using linear scan
            
        - Time: O(n) where n is the number of troops
        - Space: O(1)
            
        Why linear scan instead of utilizing a sorted grid such as the one we have due to the visualization
        - Finding closest requires 2D Euclidean distance, not 1D sorting
        - With ~50 troops max, O(n) scan is faster than maintaining spatial indices
        - Troops move every frame, so index updates would cost more than linear scan saves
        """
        closest_troop = None
        minimum_distance = inf
                
        for troop in self.arena.unique_troops:
            #troop = occupancy_grid[cell]
            # skip if already checked, same team, or dead
            if troop.team == self.team or not troop.is_alive:
                continue
            if troop.troop_can_fly and not self.troop_can_target_air:
                continue # the troop can't see the target
            
            if self.troop_favorite_target != "any" and troop.troop_type != self.troop_favorite_target:
                # we only target the favourite target types
                continue
            
            # using center-to-center distance for consistency
            distance = calculate_edge_to_edge_distance(self, troop)
            
            if distance < minimum_distance:
                minimum_distance = distance
                closest_troop = troop
        
        return minimum_distance, closest_troop

    def occupied_cells(self):
        """
        Returns dictionary of all cells this troop occupies

        - Time: Worst case = Average case = O(tw * th) where tw/th are troop width and height iterates over all cells
        - Space: O(tw * th) for dictionary entries
        """
        occupancy_grid = {}
        if self.location is None or self.arena is None:
            raise ValueError("Location and arena must be set before calling occupied_cells")

        base_row, base_col = self.location # (top left corner)
        for row in range(base_row, base_row + self.height):
            for col in range(base_col, base_col + self.width):
                if is_cell_in_bounds((row, col), self.arena.grid):
                    occupancy_grid[(row, col)] = self
        
        return occupancy_grid

    """SPRITE LOADING"""
    def swap_sprite(self, moving=True, reset_attack=False):
        """
        Cycles through sprite animations (moving/attack states) and loads appropriate sprite

        - Time: Worst case = Average case = O(1) cached, O(w*h) on first load where w*h=256^2=65k pixels for file I/O/standardization
        - Space: O(w*h) per sprite surface in cache (65k pixels typical)

        Note: By default the frame count check is always true (integer % 1 == 0), so runs every call
        """
        if self.arena.frame_count % ANIMATION_RATE == 0:
            if moving:
                if self.sprite_number >= 1: # we have 3 sprites so we cycle through them but 0 and 1 are movement and 2 is attack  
                    self.sprite_number = 0 # moving sprite 1
                else:
                    self.sprite_number = 1 # moving sprite 2
            
            elif reset_attack:
                self.sprite_number = 0 # so we reset the attack sprite to the first one
            else:
                self.sprite_number = 2 # attack sprite

            self.sprite = self.asset_manager.get_troop_sprite(self.name, self.team, self.sprite_number)

    """MAIN FUNCTIONS"""
    def move_to_tower(self, got_blocked=False):
        """
        Main movement logic: finds target, paths to it, moves along path and if close enough attacks
        
        - Time: Worst case = Average case = O(n + V + E) where:
            - n is troop count for find_closest_enemy_troop linear scan
            - V + E for BFS pathfinding (V = grid cells, E = edges up to 8V)
        - Space: O(V) for path storage and BFS visited set

        NOTE:Uses BFS for pathfinding because it guarantees shortest path on unweighted grids
        """
        if not self.is_active or not self.is_alive:
            return
        
        path = None

        if not self.is_targetting_something:
            # we first check if something can be targetted
            # let's see if we can attack something near us
            self.in_process_attack = None # remember to reset the attack state
            path = self.find_closest_target(got_blocked=got_blocked) # this will return the path to the option we are going for 

        if self.is_targetting_something: # if we are now targetting something we do this instead of moving torward the towers
            if not self.is_targetting_something.is_alive:
                self.is_targetting_something = None # we reset the target because the target is dead
                self.reset_path()
                path = self.find_closest_target()
        
            else:
                # we overwrite the path to the tower to the one to the troop
                # if it is still alive then
                # make sure that the troop is still in range of the troop that it is attacking if not walk there
                if not is_in_attack_range(self, self.is_targetting_something):
                    self.reset_path()
                    target_grid = self.is_targetting_something.get_occupancy_grid()
                    self.in_process_attack = None

                    if self.raw_movement_speed > 0:
                        #print(f"{self.name} not in range, finding pabth to troop")
                        path = find_path_bfs(self.location, self.arena.grid, self.get_occupancy_grid(), target_grid, self, cell_type=self.is_targetting_something)
                        #print(f"{self.name} trying to path to {self.is_targetting_something.name}", path)
                        self.current_path = path
                    else:
                        self.is_targetting_something = None # we reset the target because the target is far away and we can't move
                else:
                    #if self.movement_speed != 0:
                        #print(f"{self.name} already in range, no need to move, Attacking")
                    path = None
                    self.attack()

        if self.raw_movement_speed == 0:
            return 

        if not path:
            #print("reached objective")
            self.reset_path() # we cleanup because the path is not valid anymore
            return

        if not got_blocked:
            self.movement_accumulator += self.raw_movement_speed
        
        if self.movement_accumulator < 1:
            return 

        # calculate how many steps needed
        # path includes start position, so actual steps = len(path) - 1
        # we want to stop when within attack_range of target
        steps_done = 0 + self.current_path_index
        #print(f"{self.name} has accumulated {self.movement_accumulator} steps")
        self.in_process_attack = None

        while self.movement_accumulator >= 1.0:
            # start from index 1 not 0 so we avoid the same cell 
            steps_done = steps_done + 1 

            if steps_done >= len(path):
                #print("path not long enough")
                self.reset_path() # we cleanup because we finished the path
                return 
            
            if self.is_targetting_something is not None and is_in_attack_range(self, self.is_targetting_something):
                #print(f"{self.name} is in attack range of {self.is_targetting_something.name}, no need to move, attacking")
                self.attack()
                return
            
            if not self.arena.move_unit(self, path[steps_done]):
                #print("Unit in the way checking again path considering troops")  
                self.reset_path()
                if got_blocked:
                    self.is_targetting_something = None # we can't get to the target 
                    return
                self.move_to_tower(got_blocked=True)
                return

            else:
                self.movement_accumulator -= 1.0 # we moved so we need to consume it
                #print(f"{self.name} moves to {path[steps_done]}")
                self.current_path_index = steps_done
                self.location = path[steps_done]  
                self.swap_sprite(moving=True)
    
    def attack(self):
        """
        Handles attack timing and damage application in area of effect

        - Time: Worst case = Average case = O(r^2) where r is attack_tile_radius checks cells in square around target
        - Space: O(1) no additional allocations
        """
        if self.is_alive and self.is_active:
            if self.in_process_attack:
                if not self.is_targetting_something:
                    return False # for some reason the troop is not targetting something, we return false

                if (self.arena.frame_count-self.in_process_attack) >= self.attack_speed:
                    # attack_tile_radius
                    # we expand the damage in all directions from the location of this troop
                    # we do the damage based on location and not on troop targetted we use that only for the initial "explosion"
                    self.swap_sprite(moving=False, reset_attack=False)
                    loc = self.is_targetting_something.location
                    is_the_target_air = self.is_targetting_something.troop_can_fly
                    for i_row in range(0-self.attack_tile_radius, self.attack_tile_radius+1):
                        for i_col in range(0-self.attack_tile_radius, self.attack_tile_radius+1):
                            # we need to check both occupancy grids if the troop is able to attack air, otherwise only the ground one
                            loc_to_check = (loc[0]+i_row, loc[1]+i_col)

                            if self.troop_can_target_air and (is_the_target_air or self.attack_tile_radius>0):
                                if loc_to_check in self.arena.occupancy_grid_flying:
                                    if self.arena.occupancy_grid_flying[loc_to_check] != self and self.team != self.arena.occupancy_grid_flying[loc_to_check].team:
                                        self.arena.occupancy_grid_flying[loc_to_check].take_damage(self.damage, source_troop=self)

                                        if self.attack_tile_radius == 0:
                                            continue # we don't want to do damage in both ground and air cells if the radius is 0

                            if loc_to_check in self.arena.occupancy_grid:
                                if self.arena.occupancy_grid[loc_to_check] != self and self.team != self.arena.occupancy_grid[loc_to_check].team:
                                    self.arena.occupancy_grid[loc_to_check].take_damage(self.damage, source_troop=self)

                    #self.is_targetting_something.take_damage(self.damage, source_troop=self) old system
                    self.in_process_attack = None
                    return True
            
                elif (self.arena.frame_count-self.in_process_attack) >= self.attack_speed * 0.70:
                    self.swap_sprite(moving=False, reset_attack=False)  # attack sprite (windup before hit)
            
                elif (self.arena.frame_count-self.in_process_attack) >= self.attack_speed * 0.40:
                    self.swap_sprite(moving=False, reset_attack=True)  # idle sprite (charging)
            
            
            else:
                self.in_process_attack = self.arena.frame_count
                self.swap_sprite(moving=True)

            return True
        print(f"{self.name} is dead or inactive, cannot attack")
        return False

    def take_damage(self, damage, source_troop=None):
        """
        Applies damage and handles death/removal

        - Time: Worst case O(tw * th), Average case O(1) if unit survives, O(tw * th) if unit dies for removal
        - Space: O(1) no additional space
        """
        if self.health - damage <= 0:
            self.is_alive = False
            if self.is_tower:
                self.arena.remove_tower(self) # tower has a different cleanup function
            else:
                self.arena.remove_unit(self)
        else:
            self.health -= damage
            #print(f"{self.name} of team {self.team} takes {damage} damage from {source_troop.name} of team {source_troop.team}, {self.health} health left")