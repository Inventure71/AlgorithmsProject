from arena.arena import Arena
from deck.card import Card
from deck.deck import Deck
from player import Player
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

cards = [Card(name="card1", cost=1, color="red", troop_name="barbarian"), 
    Card(name="card2", cost=2, color="blue", troop_name="barbarian"),
    Card(name="card3", cost=3, color="green", troop_name="barbarian"),
    Card(name="card4", cost=4, color="yellow", troop_name="barbarian"),
    Card(name="card5", cost=5, color="purple", troop_name="barbarian"),
    Card(name="card6", cost=6, color="orange", troop_name="barbarian"),
    Card(name="card7", cost=7, color="red", troop_name="barbarian"),
    Card(name="card8", cost=8, color="blue", troop_name="barbarian"),
    Card(name="card9", cost=9, color="green", troop_name="barbarian"),
    Card(name="card10", cost=10, color="yellow", troop_name="barbarian")]

deck = Deck(cards)
deck.shuffle_cards()

"""
Modifiable variables for the game loop
"""
rows = int(32) #32
cols = int(rows / 16 * 9)
draw_borders = True
hand_area_height = 100


"""
Global variables for the game loop
"""
screen = None
clock = None
arena = None
tile_size = None
selected_card = None

player_1 = Player(name="Player 1", deck=deck, team=1, arena=arena)
player_2 = Player(name="Player 2", deck=deck, team=2, arena=arena)

def setup_arena():
    global screen, clock, arena, tile_size
    # find optimal tile size
    tile_size = 800/rows # optimal for 32 is 25

    pygame.init()

    screen = pygame.display.set_mode((int(cols * tile_size), int(rows * tile_size) + hand_area_height))
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

def draw_hand(player):
    """Draw the player's hand at the bottom of the screen"""
    if not player.hand:
        return
    
    card_width = 80
    card_height = 90
    card_spacing = 10
    hand_start_y = int(rows * tile_size) + 5  # Start just below arena
    
    # Calculate starting x to center the hand
    total_width = len(player.hand) * card_width + (len(player.hand) - 1) * card_spacing
    start_x = (int(cols * tile_size) - total_width) // 2
    
    card_rects = []  # Store rects for click detection
    
    for i, card in enumerate(player.hand):
        x = start_x + i * (card_width + card_spacing)
        y = hand_start_y
        
        # Card background
        card_rect = pygame.Rect(x, y, card_width, card_height)
        card_rects.append((card_rect, card))
        
        # Highlight selected card
        if card == selected_card:
            pygame.draw.rect(screen, (255, 255, 0), card_rect, 3)  # Yellow border
            pygame.draw.rect(screen, (100, 100, 100), card_rect)  # Darker background
        else:
            pygame.draw.rect(screen, (150, 150, 150), card_rect)  # Gray background
            pygame.draw.rect(screen, (200, 200, 200), card_rect, 2)  # Light border
        
        # Draw card color indicator (top portion)
        color_rect = pygame.Rect(x, y, card_width, 20)
        pygame.draw.rect(screen, card.color, color_rect)
        
        # Draw card name (simple text - you may want to use pygame.font for better text)
        # For now, just show first letter or use a simple representation
        font = pygame.font.Font(None, 24)
        name_text = font.render(card.name[:8], True, (0, 0, 0))  # Truncate long names
        screen.blit(name_text, (x + 5, y + 25))
        
        # Draw cost
        cost_text = font.render(f"Cost: {card.cost}", True, (0, 0, 0))
        screen.blit(cost_text, (x + 5, y + 50))
    
    return card_rects

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

    card_rects = draw_hand(player_1)
    pygame.display.flip()
    clock.tick(60)

pygame.quit()