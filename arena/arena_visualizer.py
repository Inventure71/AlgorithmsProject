from arena import Arena
import pygame



colors = {
    0: (0, 0, 0),  # none
    1: (0, 214, 47),  # grass
    2: (0, 157, 214),  # water
    3: (133, 133, 133),   # bridge
    4: (191, 143, 36) # tower
}

rows = 16 #32
cols = int(rows / 16 * 9)
tile_size = 25 # for now

pygame.init()

screen = pygame.display.set_mode((cols * tile_size, rows * tile_size))
clock = pygame.time.Clock()

arena = Arena(rows)
arena.world_generation()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

    screen.fill((0, 0, 0))
    for y, row in enumerate(arena.grid):
        for x, value in enumerate(row):
            rect = pygame.Rect(x * tile_size, y * tile_size, tile_size, tile_size)
            # Fill tile
            pygame.draw.rect(screen, colors[value], rect)
            # Draw border (white, thickness 1)
            pygame.draw.rect(screen, (255, 255, 255), rect, 1)
    pygame.display.flip()
    clock.tick(60)

pygame.quit()