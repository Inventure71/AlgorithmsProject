
# must be bigger equal than 1
TICK_RATE = 1 # N frames per tick (meaning if N = 5, we will tick every 5 frames)

EMPTY=0; GRASS=1; WATER=2; BRIDGE=3; TOWER_P1=5; TOWER_P2=8 
walkable_cells = set([GRASS, BRIDGE])
flyable_cells = set([GRASS, BRIDGE, WATER])
BASE_GRID_HEIGHT = 32 # in cells (min is 32) maintain constant, change the multiplier
MULTIPLIER_GRID_HEIGHT = int(2) # the number we multiply the base grid height by to get the actual grid height

# this is just for efficency purposes, don't modify
GAP_BETWEEN_TOWER_CELLS = 1 # this is the multiple of the number of cells to not add for example 3 would mean 1 every 3 is added to the occupancy grid

DRAW_BORDERS = True
HAND_AREA_HEIGHT = 140
ARENA_BACKGROUND_USE_IMAGE = True
DRAW_ATTACK_RANGES_DEBUG = False 

TICKS_PER_SECOND = 60

