
TICK_RATE = 1 # N frames per tick (meaning if N = 5, we will tick every 5 frames)


EMPTY=0; GRASS=1; WATER=2; BRIDGE=3; TOWER_P1=4; TOWER_P2=5
walkable_cells = [GRASS, BRIDGE]
BASE_GRID_HEIGHT = 32 # in cells (min is 32)
MULTIPLIER_GRID_HEIGHT = 2 # the number we multiply the base grid height by to get the actual grid height

DRAW_BORDERS = True
HAND_AREA_HEIGHT = 100
ARENA_BACKGROUND_USE_IMAGE = True
DRAW_ATTACK_RANGES_DEBUG = True 

