from deck.stats import stats

class Card:
    def __init__(self, 
    name, 
    cost, 
    color, 
    troop_class,
    troop_name):
        self.name = name
        self.cost = cost
        self.troop_class = troop_class
        self.color = color

        self.troop_name = troop_name
        if troop_name in stats:
            self.troop_health = stats.get(troop_name).get("troop_health")
            self.troop_damage = stats.get(troop_name).get("troop_damage")
            self.troop_movement_speed = stats.get(troop_name).get("troop_movement_speed")
            self.troop_attack_type = stats.get(troop_name).get("troop_attack_type")
            self.troop_attack_speed = stats.get(troop_name).get("troop_attack_speed")
            self.troop_attack_range = stats.get(troop_name).get("troop_attack_range")
            self.troop_attack_aggro_range = stats.get(troop_name).get("troop_attack_aggro_range")
            self.troop_attack_cooldown = stats.get(troop_name).get("troop_attack_cooldown")
            self.troop_width = stats.get(troop_name).get("troop_width")
            self.troop_height = stats.get(troop_name).get("troop_height")

        else:
            raise ValueError(f"Troop {troop_name} not found in stats")

    def create_troop(self, team):
        self.troop = self.troop_class(
            name=self.troop_name, 
            health=self.troop_health, 
            damage=self.troop_damage, 
            movement_speed=self.troop_movement_speed, 
            attack_type=self.troop_attack_type, 
            attack_speed=self.troop_attack_speed, 
            attack_range=self.troop_attack_range, 
            attack_aggro_range=self.troop_attack_aggro_range,
            attack_cooldown=self.troop_attack_cooldown, 
            width=self.troop_width, 
            height=self.troop_height, 
            color=self.color, 
            team=team)
        return self.troop
    