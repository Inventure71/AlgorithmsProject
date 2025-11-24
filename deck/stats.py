

stats_barbarian = {
    "troop_health": 100, 
    "troop_damage": 10, 
    "troop_movement_speed": 0.2, 
    "troop_attack_type": "melee", 
    "troop_attack_speed": 60, 
    "troop_attack_range": 1, 
    "troop_attack_aggro_range": 5,
    "troop_attack_cooldown": 1, 
    "troop_type": "troop",
    "troop_favorite_target": "any",
    "troop_width": 1,
    "troop_height": 1,
    "troop_cost": 5,
    "troop_count": 4,
    "scale_multiplier": 0.5,
}

stats_archer= {
    "troop_health": 50, 
    "troop_damage": 5, 
    "troop_movement_speed": 0.2, 
    "troop_attack_type": "ranged", 
    "troop_attack_speed": 45, 
    "troop_attack_range": 3, 
    "troop_attack_aggro_range": 5,
    "troop_attack_cooldown": 1, 
    "troop_type": "troop",
    "troop_favorite_target": "any",
    "troop_width": 1,
    "troop_height": 1,
    "troop_cost": 2,
    "troop_count": 2,
    "scale_multiplier": 0.5,
}

stats_tower_small = {
    "troop_health": 2000,
    "troop_damage": 10,
    "troop_movement_speed": 0,
    "troop_favorite_target": "any",
    "troop_attack_type": "melee",
    "troop_attack_speed": 60,
    "troop_attack_range": 9, # towers are the only troop that doesn't have an aggro range, they use the troop attack range
    "troop_attack_cooldown": 60,
    "troop_type": "building",
    "troop_width": 3,
    "troop_height": 3,
    "troop_cost": 0,
}

stats_tower_center = {
    "troop_health": 4000,
    "troop_damage": 10,
    "troop_movement_speed": 0, 
    "troop_attack_speed": 60,
    "troop_attack_range": 9, # towers are the only troop that doesn't have an aggro range, they use the troop attack range
    "troop_attack_cooldown": 1,
    "troop_type": "building",
    "troop_favorite_target": "any",
    "troop_width": 4,
    "troop_height": 4,
    "troop_cost": 0,
}

stats = {
    "barbarian": stats_barbarian,
    "archer": stats_archer,
}