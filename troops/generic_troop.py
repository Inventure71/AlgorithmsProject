import random
from tkinter import NO
from arena.utils.find_path_bfs import find_path_bfs


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
    
    def move_v1(self): # row, col
        # move in that direction on the board

        if self.team == 1:
            direction = (-1, 0)
        else:
            direction = (1, 0)

        target_cell = (self.location[0] + direction[0], self.location[1] + direction[1])
        
        if not self.arena.move_unit(self, target_cell):
            print("ERROR MOVING")

    def move_random_target(self):
        if  not self.target or self.location == self.target:
            self.target = (random.randint(0, self.arena.height-1), random.randint(0, self.arena.width-1))
        
        path = find_path_bfs(self.location, self.arena, goal_cell=self.target)
        
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


        