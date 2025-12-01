from UI.components.arena_ui import draw_arena, draw_units
from UI.components.hand_ui import draw_hand, draw_elixir_icon
from UI.components.debug_ui import draw_attack_ranges
from UI.finish_battle_screen import FinishBattleScreen
from UI.menu import run_deck_builder
from arena.arena import Arena
from constants import *
from deck.card import Card
from deck.deck import Deck
from player import Player
from troops.generic_troop import Troop
from assets.asset_manager import AssetManager
import pygame
from troops.bot import GreedyBot

colors = {
    0: (0, 0, 0),  # none
    1: (0, 214, 47),  # grass
    2: (0, 157, 214),  # water
    3: (133, 133, 133),   # bridge
    4: (191, 143, 36), # tower p1
    5: (200, 100, 100), # tower p2
    9: (200, 100, 100, 100) # transparent red
}

"""
Modifiable variables for the game loop
"""
rows = int(BASE_GRID_HEIGHT*MULTIPLIER_GRID_HEIGHT)
cols = int(rows / 16 * 9)
DRAW_PLACABLE_CELLS = True


"""
Global variables for the game loop
"""
looping = True
screen = None
clock = None
arena = None
tile_size = None
selected_card = None
card_rects = []
time_location = None
arena_background_surface = None
arena_background_dirty = True
asset_manager = AssetManager()
bot = None

def setup_arena():
    """
    Initializes pygame and creates the arena

    - Time: Worst case = Average case = O(h * w) for arena grid creation and world generation
    - Space: O(h * w) for arena grid
    """
    global screen, clock, arena, tile_size, asset_manager, time_location
    # find optimal tile size
    tile_size = 800/rows # optimal for 32 is 25

    time_location = (int(cols * tile_size) - 50, 10)

    pygame.init()

    screen = pygame.display.set_mode((int(cols * tile_size), int(rows * tile_size) + HAND_AREA_HEIGHT))
    clock = pygame.time.Clock()

    arena = Arena(rows)
    arena.asset_manager = asset_manager
    arena.world_generation()
    arena.arena_background_dirty = True

def game_tick():
    """
    Processes one game tick - updates all troop movements

    - Time: Worst case = Average case = O(n * (n + V + E)) where:
        - n is the number of active troops
        - For each troop: O(n) linear scan to find closest enemy + O(V + E) BFS pathfinding
        - V = h * w grid cells, E = up to 8V edges for 8-directional movement
    - Space: O(V) per troop for path storage, O(n * V) total in worst case
    """
    # only every N frames
    if arena.frame_count % TICK_RATE == 0:
        for troop in list(arena.unique_troops):
            troop.move_to_tower()

"""FONT"""
def get_font(font_size=24):
    return asset_manager.get_font(font_size)

"""GAME LOOP"""
while looping: # bigger loop for the game loop

    cards = [
    Card(name="barbarian 1", color="red", troop_class=Troop, troop_name="barbarian", asset_manager=asset_manager), 
    Card(name="archer 1", color="orange", troop_class=Troop, troop_name="archer", asset_manager=asset_manager),
    Card(name="giant 1", color="yellow", troop_class=Troop, troop_name="giant", asset_manager=asset_manager),
    Card(name="goblins 1", color="purple", troop_class=Troop, troop_name="goblins", asset_manager=asset_manager),
    Card(name="dart goblin 1", color="blue", troop_class=Troop, troop_name="dart goblin", asset_manager=asset_manager),
    Card(name="elite barbs 1", color="yellow", troop_class=Troop, troop_name="elite barbs", asset_manager=asset_manager),
    Card(name="knight 1", color="orange", troop_class=Troop, troop_name="knight", asset_manager=asset_manager),
    Card(name="mini pekka 1", color="blue", troop_class=Troop, troop_name="mini pekka", asset_manager=asset_manager),
    Card(name="musketeer 1", color="yellow", troop_class=Troop, troop_name="musketeer", asset_manager=asset_manager),
    Card(name="pekka 1", color="orange", troop_class=Troop, troop_name="pekka", asset_manager=asset_manager),
    Card(name="bats 1", color="green", troop_class=Troop, troop_name="bats", asset_manager=asset_manager),
    Card(name="skeleton 1", color="green", troop_class=Troop, troop_name="skeletons", asset_manager=asset_manager),
    ]

    setup_arena()
    deck_p1 = run_deck_builder(screen, asset_manager)
    if deck_p1 is None:
        break

    deck_p1.shuffle_cards()
    deck_p2 = Deck(cards)
    deck_p2.shuffle_cards()

    finish_battle_screen = None
    
    player_1 = Player(name="Player 1", deck=deck_p1, team=1, arena=arena)
    player_2 = Player(name="Player 2", deck=deck_p2, team=2, arena=arena) 
    player_1.setup_hand()
    player_2.setup_hand()

    bot = GreedyBot(player_2, arena)

    # the loop only works for player 1 input for now
    while True:
        if not arena.tick():
            print("Match over")
            break

        # here we handle pygame events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            
            # left click
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1: # left Mouse Button
                    mouse_pos = pygame.mouse.get_pos() # get position on screen
                    click_handled = False

                    for rect, card in card_rects:
                        if rect.collidepoint(mouse_pos):
                            if selected_card == card:
                                selected_card = None
                                print(f"De selected: {card.name}")
                            else:
                                if card.cost <= player_1.current_elixir:
                                    selected_card = card
                                    print(f"Selected: {card.name}")
                                else:
                                    print(f"Not enough elixir to select: {card.name}")
                            
                            click_handled = True
                            break # found the event, stop searching
                    
                    if not click_handled and selected_card is not None: # which means not in the cards area and we have a selected card
                        # we convert to the grid, but now we need to check if it is in that grid
                        clicked_row = int(mouse_pos[1] // tile_size)
                        clicked_col = int(mouse_pos[0] // tile_size)

                        # check boundaries 
                        if arena.is_placable_cell(clicked_row, clicked_col, 1, is_flying=selected_card.troop_can_fly):
                            print(f"Trying to place troop at {clicked_row}, {clicked_col}")
                            
                            # player 
                            if not player_1.place_troop((clicked_row, clicked_col), selected_card):
                                continue
                            
                            # deselect after playing
                            selected_card = None

                            click_handled = True # in case we add other statments later 
                    
        #if arena.frame_count % 100 == 0 and selected_card is not None:
        #    player_2.place_troop((3, 3), selected_card)
        
        if arena.frame_count % 2 == 0:
            bot_card, bot_position = bot.think()
            if bot_card and bot_position:
                player_2.place_troop(bot_position, bot_card)
  

        player_1.increase_elixir()    
        player_2.increase_elixir()

        screen.fill((66, 49, 22))
        draw_arena(cols, rows, tile_size, asset_manager, screen, arena, selected_card=selected_card, team=1)        
        game_tick()
        draw_units(arena, screen, tile_size, asset_manager)

        if DRAW_ATTACK_RANGES_DEBUG:
            draw_attack_ranges(arena, tile_size, screen)

        card_rects = draw_hand(player_1, rows, cols, tile_size, asset_manager, screen, selected_card=selected_card)

        font = get_font(30)
        fps_surface = font.render(f"FPS: {clock.get_fps():.1f}", True, (255, 255, 255))
        screen.blit(fps_surface, (10, 10))

        """TIME LEFT"""
        time_left_surface = font.render(f"{(arena.time_left//arena.one_minute)}:{((arena.time_left%arena.one_minute)//TICKS_PER_SECOND):02d}", True, (255, 255, 255))
        screen.blit(time_left_surface, time_location)
        
        """ELIXIR MULTIPLIER"""
        if arena.elixir_multiplier != 1:
            draw_elixir_icon(
                time_location[0],
                time_location[1] + 20,
                40,
                asset_manager,
                screen,
                text_value=f"x{arena.elixir_multiplier:.1f}",
            )

        pygame.display.flip()
        clock.tick(TICKS_PER_SECOND+1) # we add 1 to have a bit of a margin, sometimes it goes a bit slow
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    mouse_pos = pygame.mouse.get_pos()
                    for button in finish_battle_screen.buttons:
                        button.is_clicked(mouse_pos)

        print("Match over")
        draw_arena(cols, rows, tile_size, asset_manager, screen, arena, selected_card=selected_card, team=1)
        draw_units(arena, screen, tile_size, asset_manager)

        if finish_battle_screen is None:
            finish_battle_screen = FinishBattleScreen(arena, asset_manager, screen)

        if finish_battle_screen.restart_clicked:
            break
        
        if finish_battle_screen.main_menu_clicked:
            looping = False
            break

        finish_battle_screen.draw()
        pygame.display.flip()

        clock.tick(TICKS_PER_SECOND+1)

pygame.quit()
exit()