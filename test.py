

"""
TODO: test the find_path_bfs function

TODO: make find_path_bfs not use arena at all but a grid instead so we can modify the grid given to it


"ACTUAL ONES"
TODO: add win situation and replay button
TODO: add tower animations and destructed building
TODO: add timer for the battle and suddendeath sitation
"""


damage_per_attack = 119
damage_per_second = 79
frames_per_second = 60 # expected 


#damage_per_second * second = damage_per_attack * attacks_x_second
#damage_per_second * frames_per_second = damage_per_attack * attacks_x_second

attacks_x_second = (damage_per_attack * frames_per_second) / damage_per_second

print(attacks_x_second)



