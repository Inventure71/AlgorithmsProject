
""" CORRECTlY BALANCED
stats_barbarian = {
    "troop_health": 262, 
    "troop_damage": 10, 
    "troop_movement_speed": 0.05, 
    "troop_attack_type": "melee", 
    "troop_attack_speed": 79, 
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
    "troop_health": 119, 
    "troop_damage": 39, 
    "troop_movement_speed": 0.05, 
    "troop_attack_type": "ranged", 
    "troop_attack_speed": 54, 
    "troop_attack_range": 3, 
    "troop_attack_aggro_range": 5,
    "troop_attack_cooldown": 1, 
    "troop_type": "troop",
    "troop_favorite_target": "any",
    "troop_width": 1,
    "troop_height": 1,
    "troop_cost": 3,
    "troop_count": 2,
    "scale_multiplier": 0.5,
}

stats_giant = {
    "troop_health": 1933,
    "troop_damage": 119,
    "troop_movement_speed": 0.04,
    "troop_attack_type": "melee",
    "troop_attack_speed": 90,
    "troop_attack_range": 1,
    "troop_attack_aggro_range": 5,
    "troop_attack_cooldown": 1, 
    "troop_type": "troop",
    "troop_favorite_target": "building",
    "troop_width": 1,
    "troop_height": 1,
    "troop_cost": 5,
    "troop_count": 1,
    "scale_multiplier": 1,
}
stats_tower_small = {
    "troop_health": 1400,
    "troop_damage": 50,
    "troop_movement_speed": 0,
    "troop_favorite_target": "any",
    "troop_attack_type": "melee",
    "troop_attack_speed": 48,
    "troop_attack_range": 9, # towers are the only troop that doesn't have an aggro range, they use the troop attack range
    "troop_attack_cooldown": 1,
    "troop_type": "building",
    "troop_width": 3,
    "troop_height": 3,
    "troop_cost": 0,
}

stats_tower_center = {
    "troop_health": 2400,
    "troop_damage": 50,
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
""" 


"""TO BALANCE"""
stats_barbarian = {
    "troop_health": 555,
    "troop_damage": 159,
    "troop_movement_speed": 0.04,
    "troop_attack_type": "melee",
    "troop_attack_speed": 78,
    "troop_attack_range": 1,
    "troop_attack_aggro_range": 5,
    "troop_attack_cooldown": 1,
    "troop_type": "troop",
    "troop_favorite_target": "any",
    "troop_width": 1,
    "troop_height": 1,
    "troop_cost": 5,
    "troop_count": 5,
    "scale_multiplier": 0.5
}
stats_archer = {
    "troop_health": 252,
    "troop_damage": 89,
    "troop_movement_speed": 0.04,
    "troop_attack_type": "ranged",
    "troop_attack_speed": 72,
    "troop_attack_range": 3,
    "troop_attack_aggro_range": 5,
    "troop_attack_cooldown": 1,
    "troop_type": "troop",
    "troop_favorite_target": "any",
    "troop_width": 1,
    "troop_height": 1,
    "troop_cost": 3,
    "troop_count": 2,
    "scale_multiplier": 0.5
}

stats_giant = {
    "troop_health": 3275,
    "troop_damage": 211,
    "troop_movement_speed": 0.03,
    "troop_attack_type": "melee",
    "troop_attack_speed": 90,
    "troop_attack_range": 1,
    "troop_attack_aggro_range": 5,
    "troop_attack_cooldown": 1,
    "troop_type": "troop",
    "troop_favorite_target": "building",
    "troop_width": 1,
    "troop_height": 1,
    "troop_cost": 5,
    "troop_count": 1,
    "scale_multiplier": 1
}

stats_goblins = {
    "troop_health": 167,
    "troop_damage": 99,
    "troop_movement_speed": 0.07,
    "troop_attack_type": "melee",
    "troop_attack_speed": 66,
    "troop_attack_range": 1,
    "troop_attack_aggro_range": 5,
    "troop_attack_cooldown": 1,
    "troop_type": "troop",
    "troop_favorite_target": "any",
    "troop_width": 1,
    "troop_height": 1,
    "troop_cost": 2,
    "troop_count": 4,
    "scale_multiplier": 1
}
stats_dart_goblin = {
    "troop_health": 216,
    "troop_damage": 131,
    "troop_movement_speed": 0.07,
    "troop_attack_type": "ranged",
    "troop_attack_speed": 41,
    "troop_attack_range": 6.5,
    "troop_attack_aggro_range": 7,
    "troop_attack_cooldown": 1,
    "troop_type": "troop",
    "troop_favorite_target": "any",
    "troop_width": 1,
    "troop_height": 1,
    "troop_cost": 3,
    "troop_count": 1,
    "scale_multiplier": 1
}
stats_elite_barbs = {
    "troop_health": 1100,
    "troop_damage": 310,
    "troop_movement_speed": 0.07,
    "troop_attack_type": "melee",
    "troop_attack_speed": 90,
    "troop_attack_range": 1,
    "troop_attack_aggro_range": 6,
    "troop_attack_cooldown": 1,
    "troop_type": "troop",
    "troop_favorite_target": "any",
    "troop_width": 1,
    "troop_height": 1,
    "troop_cost": 6,
    "troop_count": 2,
    "scale_multiplier": 1
}
stats_knight = {
    "troop_health": 1450,
    "troop_damage": 167,
    "troop_movement_speed": 0.04,
    "troop_attack_type": "melee",
    "troop_attack_speed": 71,
    "troop_attack_range": 1,
    "troop_attack_aggro_range": 5,
    "troop_attack_cooldown": 1,
    "troop_type": "troop",
    "troop_favorite_target": "any",
    "troop_width": 1,
    "troop_height": 1,
    "troop_cost": 3,
    "troop_count": 1,
    "scale_multiplier": 1
}
stats_mini_pekka = {
    "troop_health": 1129,
    "troop_damage": 650,
    "troop_movement_speed": 0.06,
    "troop_attack_type": "melee",
    "troop_attack_speed": 108,
    "troop_attack_range": 1,
    "troop_attack_aggro_range": 5,
    "troop_attack_cooldown": 1,
    "troop_type": "troop",
    "troop_favorite_target": "any",
    "troop_width": 1,
    "troop_height": 1,
    "troop_cost": 4,
    "troop_count": 1,
    "scale_multiplier": 1
}
stats_musketeer = {
    "troop_health": 640,
    "troop_damage": 190,
    "troop_movement_speed": 0.04,
    "troop_attack_type": "ranged",
    "troop_attack_speed": 65,
    "troop_attack_range": 6,
    "troop_attack_aggro_range": 6,
    "troop_attack_cooldown": 1,
    "troop_type": "troop",
    "troop_favorite_target": "any",
    "troop_width": 1,
    "troop_height": 1,
    "troop_cost": 4,
    "troop_count": 1,
    "scale_multiplier": 1
}
stats_pekka = {
    "troop_health": 3400,
    "troop_damage": 750,
    "troop_movement_speed": 0.03,
    "troop_attack_type": "melee",
    "troop_attack_speed": 109,
    "troop_attack_range": 1,
    "troop_attack_aggro_range": 5,
    "troop_attack_cooldown": 1,
    "troop_type": "troop",
    "troop_favorite_target": "any",
    "troop_width": 1,
    "troop_height": 1,
    "troop_cost": 7,
    "troop_count": 1,
    "scale_multiplier": 1
}
stats_royal_giant = {
    "troop_health": 2800,
    "troop_damage": 290,
    "troop_movement_speed": 0.03,
    "troop_attack_type": "ranged",
    "troop_attack_speed": 102,
    "troop_attack_range": 5,
    "troop_attack_aggro_range": 5,
    "troop_attack_cooldown": 1,
    "troop_type": "troop",
    "troop_favorite_target": "building",
    "troop_width": 1,
    "troop_height": 1,
    "troop_cost": 6,
    "troop_count": 1,
    "scale_multiplier": 1
}
stats_skeletons = {
    "troop_health": 67,
    "troop_damage": 67,
    "troop_movement_speed": 0.05,
    "troop_attack_type": "melee",
    "troop_attack_speed": 60,
    "troop_attack_range": 1,
    "troop_attack_aggro_range": 5,
    "troop_attack_cooldown": 1,
    "troop_type": "troop",
    "troop_favorite_target": "any",
    "troop_width": 1,
    "troop_height": 1,
    "troop_cost": 1,
    "troop_count": 3,
    "scale_multiplier": 1
}
stats_spear_goblin = {
    "troop_health": 110,
    "troop_damage": 67,
    "troop_movement_speed": 0.07,
    "troop_attack_type": "ranged",
    "troop_attack_speed": 100,
    "troop_attack_range": 5,
    "troop_attack_aggro_range": 5.5,
    "troop_attack_cooldown": 1,
    "troop_type": "troop",
    "troop_favorite_target": "any",
    "troop_width": 1,
    "troop_height": 1,
    "troop_cost": 2,
    "troop_count": 3,
    "scale_multiplier": 1
}


"""TOWER"""

stats_tower_small = {
    "troop_health": 2534,
    "troop_damage": 90,
    "troop_movement_speed": 0,
    "troop_favorite_target": "any",
    "troop_attack_type": "ranged",
    "troop_attack_speed": 48,
    "troop_attack_range": 9,
    "troop_attack_cooldown": 1,
    "troop_type": "building",
    "troop_width": 3,
    "troop_height": 3,
    "troop_cost": 0
}
stats_tower_center = {
    "troop_health": 4008,
    "troop_damage": 90,
    "troop_movement_speed": 0,
    "troop_attack_speed": 60,
    "troop_attack_range": 9,
    "troop_attack_cooldown": 1,
    "troop_type": "building",
    "troop_favorite_target": "any",
    "troop_width": 4,
    "troop_height": 4,
    "troop_cost": 0
}

stats = {
    "barbarian": stats_barbarian,
    "archer": stats_archer,
    "giant": stats_giant,
    "goblins": stats_goblins,
    "dart goblin": stats_dart_goblin,
    "elite barbs": stats_elite_barbs,
    "knight": stats_knight,
    "mini pekka": stats_mini_pekka,
    "musketeer": stats_musketeer,
    "pekka": stats_pekka,
    "royal giant": stats_royal_giant,
    "skeletons": stats_skeletons,
    "spear goblin": stats_spear_goblin,
}