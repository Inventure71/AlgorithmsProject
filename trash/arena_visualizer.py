# main.py
import pygame
from arena import Arena, colors

# Logical grid (cells). Keep your high detail here.
rows = 32
cols = int(rows / 16 * 9)

pygame.init()

# Pick a max window size that fits your screen
info = pygame.display.Info()
max_w, max_h = info.current_w - 100, info.current_h - 100  # some margin

# Scale factor to fit the logical surface into the window
scale = min(max_w / cols, max_h / rows)
scaled_w = max(1, int(cols * scale))
scaled_h = max(1, int(rows * scale))

# Create the window at the scaled size
screen = pygame.display.set_mode((scaled_w, scaled_h), pygame.RESIZABLE)
clock = pygame.time.Clock()

# Off-screen surface at 1 px per cell (logical pixels)
logical = pygame.Surface((cols, rows))

arena = Arena(rows)
arena.world_generation()

def draw_to_logical():
    # Draw each cell as a single pixel on the logical surface
    # For speed you can batch or use surfarray later, but this is the simplest start
    for y, row in enumerate(arena.grid):
        for x, value in enumerate(row):
            logical.set_at((x, y), colors[value])

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.VIDEORESIZE:
            # Recompute scale if the user resizes the window
            sw, sh = event.w, event.h
            scale = min(sw / cols, sh / rows)
            scaled_w = max(1, int(cols * scale))
            scaled_h = max(1, int(rows * scale))
            screen = pygame.display.set_mode((scaled_w, scaled_h), pygame.RESIZABLE)

    # 1) Render the arena to the logical surface
    draw_to_logical()

    # 2) Scale logical -> screen
    scaled = pygame.transform.smoothscale(logical, (scaled_w, scaled_h))

    # 3) Blit centered (letterbox safe). Here scaled matches window, so just blit at (0, 0)
    screen.fill((0, 0, 0))
    screen.blit(scaled, (0, 0))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
