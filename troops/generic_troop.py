import random
from tkinter import NO
from constants import *
from arena.utils.random_utils import calculate_distance
from arena.utils.find_path_bfs import find_path_bfs
from arena.utils.find_path_bfs_with_range import find_path_bfs_w_range


class Troop:
    def __init__(
        self,
        name,
        health,
        damage,
        range,
        movement_speed,
        attack_type,
        attack_speed,
        attack_range,
        attack_cooldown,
        size,
        color,
        team,
        location = None,
        arena = None,
        ):
        self.name = name
        self.health = health
        self.damage = damage
        self.range = range
        self.movement_speed = movement_speed
        self.attack_speed = attack_speed
        self.attack_range = attack_range
        self.attack_cooldown = attack_cooldown
        self.size = size
        self.team = team

        self.location = location # (row, col)
        self.arena = arena

        self.color = color

        self.is_alive = True


        """EXP"""
        self.target = None
    
    def move_to_tower(self):
        tower_type = TOWER_P2 if self.team == 1 else TOWER_P1

        self.find_closest_troop(self.arena.occupancy_grid)
        
        path = find_path_bfs(self.location, self.arena.grid, {}, cell_type=tower_type)
        #if not path or len(path) <= 1:
        #    print("NO PATH FOUND TO TOWER")
        #    return
        
        moves_this_tick_to_do = self.movement_speed # 1
        moves_this_tick_done = 0
        while moves_this_tick_done < moves_this_tick_to_do:
            # start from index 1 not 0 so we avoid the same cell 
            next_index = moves_this_tick_done + 1
            if not path or next_index >= len(path):
                print("reached end of path")
                break
            
            
            if not self.arena.move_unit(self, path[moves_this_tick_done + 1]):
                print("Unit in the way checking again path considering troops")
                path = find_path_bfs(self.location, self.arena.grid, self.arena.occupancy_grid, cell_type=tower_type)
                moves_this_tick_to_do = moves_this_tick_to_do - moves_this_tick_done
                moves_this_tick_done = 0
                continue
            else:
                self.location = path[moves_this_tick_done + 1]
                moves_this_tick_done += 1
                        

    def move_random_target(self):
        if  not self.target or self.location == self.target:
            self.target = (random.randint(0, self.arena.height-1), random.randint(0, self.arena.width-1))
        
        path = find_path_bfs(self.location, self.arena.grid, self.arena.occupancy_grid, goal_cell=self.target)
        
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
        
    def find_closest_troop(self, occupancy_grid):
        for cell in occupancy_grid: # each cell contains a troop
            troop = occupancy_grid[cell]
            if troop.team != self.team:
                print("enemy troop found at distance", calculate_distance(self.location, troop.location))
            else:
                print("team troop found at distance", print("enemy troop found at distance", calculate_distance(self.location, troop.location)))
        

    def find_closest_enemy(self, enemies):
        # based on self.range see what troops are close
        pass

    def attack(self, target):
        pass

    def take_damage(self, damage):
        if self.health - damage <= 0:
            self.is_alive = False
        else:
            self.health -= damage


        