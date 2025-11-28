import pygame
from deck.card import Card
from deck.deck import Deck
from deck.stats import stats
from troops.generic_troop import Troop
from UI.components.unit_components.button import Button
from core.sorting import merge_sort_by_key 
import random


def run_deck_builder(screen, asset_manager):
    global average_elixir_cost
    average_elixir_cost = 0
    selected = []

    def calculate_average_elixir_cost():
        global average_elixir_cost
        if len(selected) == 0:
            average_elixir_cost = 0
        else:
            average_elixir_cost = sum(card.cost for card in selected) / len(selected)

    def add_card_to_deck(card):
        selected.append(card)
        calculate_average_elixir_cost()
    
    def remove_card_from_deck(card):
        if card in selected:
            selected.remove(card)
        calculate_average_elixir_cost()

    def on_sort():
        cards[:] = merge_sort_by_key(cards, key=lambda c: c.cost)

    def on_confirm(): 
        if len(selected) == 8:
            return Deck(selected.copy())
        else:
            return None

    def on_auto_fill():
        if len(selected) < 8:
            temp_unique_cards = cards.copy()
            for card in selected:
                temp_unique_cards.remove(card)
            for _ in range(8-len(selected)):
                card = random.choice(temp_unique_cards)
                add_card_to_deck(card)
                temp_unique_cards.remove(card)
            return Deck(selected.copy())
        else:
            return None    

    clock = pygame.time.Clock()
    W, H = screen.get_size()
    CW, CH, SP = 70, 80, 8
    
    cards = [Card(name=n, color="gray", troop_class=Troop, troop_name=n, asset_manager=asset_manager) for n in stats]
    scroll_y = 0
    
    deck_y = 50
    deck_bottom = deck_y + CH * 2 + SP  # bottom of the 2x4 deck grid
    cards_area_y = deck_bottom + 60
    cards_area_h = H - cards_area_y - 70
    
    # calculate background height - from top to bottom of scrolling area
    bg_height = cards_area_y + cards_area_h
    
    # get and scale background image
    bg_image = asset_manager.get_menu_background(W, bg_height)

    
    def draw_card(card, x, y, dimmed=False):
        img = card.get_card_image(CW, CH)
        if img: screen.blit(img, (x, y))
        if dimmed: screen.blit(asset_manager.get_card_overlay(CW, CH, (0, 0, 0, 160)), (x, y))
    
    
    btn_battle = Button(W//2 - 70, H - 60, 140, 45, "Battle", asset_manager.get_font(24), (50, 150, 50), on_confirm)
    btn_sort = Button(W//2 + 100, deck_bottom + 10, 60, 35, "Sort", asset_manager.get_font(18), (64, 147, 166), on_sort)
    btn_auto_fill = Button(W//2 - 165, deck_bottom + 10, 60, 35, "Auto Fill", asset_manager.get_font(18), (27, 147, 54), on_auto_fill)

    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT: return None
            if e.type == pygame.MOUSEWHEEL:
                scroll_y = max(0, scroll_y - e.y * 30)
            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                mx, my = e.pos
                btn_sort.is_clicked((mx, my))
                btn_auto_fill.is_clicked((mx, my))
                if len(selected) == 8 and btn_battle.is_clicked((mx, my)):
                    return Deck(selected.copy())
                
                # click on deck (top) to remove
                deck_x = (W - 4 * (CW + SP) + SP) // 2
                for i, c in enumerate(selected):
                    row, col = i // 4, i % 4
                    r = pygame.Rect(deck_x + col * (CW + SP), deck_y + row * (CH + SP), CW, CH)
                    if r.collidepoint(mx, my): 
                        remove_card_from_deck(c)
                        break
                
                # click on cards area to add
                if cards_area_y <= my < cards_area_y + cards_area_h:
                    grid_x = (W - 4 * (CW + SP) + SP) // 2
                    for i, c in enumerate(cards):
                        row, col = i // 4, i % 4
                        y = cards_area_y + row * (CH + SP + 15) - scroll_y
                        if y + CH < cards_area_y or y > cards_area_y + cards_area_h: continue
                        r = pygame.Rect(grid_x + col * (CW + SP), y, CW, CH)
                        if r.collidepoint(mx, my) and c not in selected and len(selected) < 8:
                            add_card_to_deck(c)
                            break
        
        # fill screen with base color first
        screen.fill((25, 20, 35))
        
        # Draw background image from top-left to top of cards area
        if bg_image:
            screen.blit(bg_image, (0, 0))
        
        # deck area (top, 2 rows of 4)
        deck_x = (W - 4 * (CW + SP) + SP) // 2
        for i in range(8):
            row, col = i // 4, i % 4
            x, y = deck_x + col * (CW + SP), deck_y + row * (CH + SP)
            pygame.draw.rect(screen, (50, 45, 60), (x, y, CW, CH), 2)
            if i < len(selected): draw_card(selected[i], x, y)
        
        btn_sort.draw(screen)
        btn_auto_fill.draw(screen)

        # we display the average elixir cost
        avg_text = f"{average_elixir_cost:.1f}"
        text_surface = asset_manager.get_text_surface(avg_text, 20, (255, 102, 204))
        text_x = W // 2 - text_surface.get_width() // 2 + 58
        text_y = deck_bottom + 10 + (35 - text_surface.get_height()) // 2 + 2
        screen.blit(text_surface, (text_x, text_y))
        
        # cards scroll area - use clipping to prevent drawing outside bounds
        scroll_clip = pygame.Rect(0, cards_area_y, W, cards_area_h)
        screen.set_clip(scroll_clip)
        
        grid_x = (W - 4 * (CW + SP) + SP) // 2
        for i, c in enumerate(cards):
            row, col = i // 4, i % 4
            x = grid_x + col * (CW + SP)
            y = cards_area_y + row * (CH + SP + 15) - scroll_y
            if y + CH < cards_area_y or y > cards_area_y + cards_area_h: continue
            draw_card(c, x, y, dimmed=(c in selected))
            # elixir cost
            screen.blit(asset_manager.get_text_surface(str(c.cost), 14, (255, 200, 255)), (x + CW//2 - 4, y + CH + 1))
        
        # reset clipping to allow drawing everywhere again
        screen.set_clip(None)
        
        # battle button
        if len(selected) == 8: btn_battle.draw(screen)
        else: pygame.draw.rect(screen, (60, 60, 60), (btn_battle.x, btn_battle.y, btn_battle.width, btn_battle.height))
        
        pygame.display.flip()
        clock.tick(60)