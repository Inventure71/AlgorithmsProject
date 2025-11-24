"""
Simple calculator to calculate framses to skip between attacks for troops
"""

damage_per_attack = 50
damage_per_second = 62
frames_per_second = 60 # expected 


#damage_per_second * second = damage_per_attack * attacks_x_second
#damage_per_second * frames_per_second = damage_per_attack * attacks_x_second

attacks_x_second = (damage_per_attack * frames_per_second) / damage_per_second

print(attacks_x_second)
