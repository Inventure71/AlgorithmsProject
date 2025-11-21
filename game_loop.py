from arena.arena import Arena
from troops.generic_troop import Troop
import pygame

colors = {
    0: (0, 0, 0),  # none
    1: (0, 214, 47),  # grass
    2: (0, 157, 214),  # water
    3: (133, 133, 133),   # bridge
    4: (191, 143, 36), # tower p1
    5: (200, 100, 100) # tower p2
}


"""
Variables for the game loop
"""
rows = int(32) #32
cols = int(rows / 16 * 9)
draw_borders = True
screen = None
clock = None
arena = None
tile_size = None

def setup_arena():
    global screen, clock, arena, tile_size
    # find optimal tile size
    tile_size = 800/rows # optimal for 32 is 25

    pygame.init()

    screen = pygame.display.set_mode((int(cols * tile_size), int(rows * tile_size)))
    clock = pygame.time.Clock()

    arena = Arena(rows)
    arena.world_generation()

def add_test_troops():
    global arena
    location = (10, 2)
    simple_troop = Troop(name="simple_troop", health=100, damage=1, range=1, movement_speed=1, attack_type="melee", attack_speed=1, attack_range=1, attack_cooldown=1, size=1, color=(255, 0, 0), team=2, location=location, arena=arena)
    arena.spawn_unit(simple_troop, location)

    location = (rows-10, 2)
    simple_troop_team_2 = Troop(name="simple_troop", health=100, damage=1, range=1, movement_speed=2, attack_type="melee", attack_speed=1, attack_range=1, attack_cooldown=1, size=1, color=(255, 0, 0), team=1, location=location, arena=arena)
    arena.spawn_unit(simple_troop_team_2, location)

def draw_arena():
    for y, row in enumerate(arena.grid):
        for x, value in enumerate(row):
            # Calculate precise pixel coordinates to avoid gaps due to float truncation
            x_pos = int(x * tile_size)
            y_pos = int(y * tile_size)
            width = int((x + 1) * tile_size) - x_pos
            height = int((y + 1) * tile_size) - y_pos
            
            rect = pygame.Rect(x_pos, y_pos, width, height)
            # Fill tile
            pygame.draw.rect(screen, colors[value], rect)
            if draw_borders:
                # Draw border (white, thickness 1)
                pygame.draw.rect(screen, (255, 255, 255), rect, 1)

def game_tick():
    for troop in list(arena.occupancy_grid.values()):
        troop.move_test()

def draw_units():
    for troop in arena.occupancy_grid.values():
        #TODO: scale the troop up like we do with the rest of the tiles 
        pygame.draw.rect(screen, troop.color, (troop.location[1] * tile_size , troop.location[0] * tile_size, tile_size, tile_size))


setup_arena()
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

    screen.fill((0, 0, 0))
    draw_arena()
    game_tick()
    draw_units()
    pygame.display.flip()
    clock.tick(60)

pygame.quit()