

class Troop:
    def __init__(
        self,
        name,
        health,
        damage,
        range,
        attack_type,
        attack_speed,
        attack_range,
        attack_cooldown,
        size,
        color,
        team,
        location,
        arena,
        ):
        self.name = name
        self.health = health
        self.damage = damage
        self.range = range
        self.attack_speed = attack_speed
        self.attack_range = attack_range
        self.attack_cooldown = attack_cooldown
        self.size = size
        self.team = team

        self.location = location # (row, col)
        self.arena = arena

        self.color = color

        self.is_alive = True
    
    def move(self): # row, col
        # move in that direction on the board

        if self.team == 1:
            direction = (-1, 0)
        else:
            direction = (1, 0)

        target_cell = (self.location[0] + direction[0], self.location[1] + direction[1])
        
        if not self.arena.move_unit(self, target_cell):
            print("ERROR MOVING")
    
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


        