import pygame
import random
from deck.card import Card
from deck.deck import Deck
from deck.stats import stats
from troops.generic_troop import Troop
from core.sorting import merge_sort_by_key 
from UI.components.hand_ui import draw_elixir_icon
from UI.components.unit_components.button import Button

"""
NOTE: The 'selected' list uses a Python list instead of a dictionary because:
- Hand size is constant (<=8 cards), making O(n) operations effectively O(1)
- Lists preserve insertion order for display consistency
- List operations like append/remove are more readable for this use case
- A dictionary would require additional key management for almost no performance benefit
"""

def run_deck_builder(screen, asset_manager):
    """
    Runs the deck builder UI - allows player to select 8 cards

    - Time: Worst case O(c log c), Average case O(c) per frame where c is card count, plus O(c log c) for sorting when triggered
    - Space: O(c) for cards list + O(8) for selected deck
    """
    global average_elixir_cost
    average_elixir_cost = 0
    selected = []

    def calculate_average_elixir_cost():
        """
        Calculates average elixir cost for the currently selected cards

        - Time: Worst case O(s), Average case O(s) where s is selected cards
        - Space: O(1)

        Uses linear sum
        """
        global average_elixir_cost
        if len(selected) == 0:
            average_elixir_cost = 0
        else:
            average_elixir_cost = sum(card.cost for card in selected) / len(selected)

    def add_card_to_deck(card):
        """
        Adds a card to the selected deck and updates average elixir cost

        - Time: Worst case O(s), Average case O(s) append plus average calculation
        - Space: O(1)
        """
        selected.append(card)
        calculate_average_elixir_cost()
    
    def remove_card_from_deck(card):
        """
        Removes a card from the selected deck and updates average elixir cost

        - Time: Worst case O(s), Average case O(s) for linear search removal
        - Space: O(1)

        Alternative: Hash table lookup would be O(1)
        """
        if card in selected:
            selected.remove(card)
        calculate_average_elixir_cost()

    def on_sort():
        """
        Sorts cards in the deck builder by elixir cost using merge sort

        - Time: Worst case O(c log c), Average case O(c log c) where c is card count
        - Space: O(c) for merge sort arrays

        Stable sort preserves equal-cost order
        """
        cards[:] = merge_sort_by_key(cards, key=lambda c: c.cost)

    def on_confirm():
        """
        Confirms the current deck selection and returns a new deck copy

        - Time: Worst case O(s), Average case O(s) where s is selected cards to copy
        - Space: O(s) for deck copy
        """
        if len(selected) == 8:
            return Deck(selected.copy())
        else:
            return None

    def on_auto_fill():
        """
        Automatically fills the deck up to 8 cards with random unique cards

        - Time: Worst case O(8-s), Average case O(8-s) random selections where s is current selected size
        - Space: O(remaining) for temporary list of available cards

        Uses random.choice for simplicity
        """
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
        """
        Time: Average case O(1) per frame using cached scaled images
              Worst case O(W*H) on first load/scale.
        Space: O(1) per call reusing cached surfaces, blits cached card image and optional overlay
        """
        img = card.get_card_image(CW, CH)
        if img: screen.blit(img, (x, y))
        if dimmed: screen.blit(asset_manager.get_card_overlay(CW, CH, (0, 0, 0, 160)), (x, y))
    
    
    btn_battle = Button(W//2 - 70, H - 160, 140, 45, "Battle", asset_manager.get_font(24), (50, 150, 50), on_confirm)
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
            if i < len(selected):
                card = selected[i]
                draw_card(card, x, y)
                icon_size = 20
                icon_x = x + (CW - icon_size) // 2
                icon_y = y + CH - icon_size + 2
                draw_elixir_icon(
                    icon_x,
                    icon_y,
                    icon_size,
                    asset_manager,
                    screen,
                    text_value=card.cost,
                    text_size=14,
                )
        
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
            if y + CH < cards_area_y or y > cards_area_y + cards_area_h: 
                continue

            draw_card(c, x, y, dimmed=(c in selected))

            # elixir icon + cost under each card (Clash Royale style)
            icon_size = 20
            icon_x = x + (CW - icon_size) // 2
            icon_y = y + CH - icon_size + 2
            draw_elixir_icon(
                icon_x,
                icon_y,
                icon_size,
                asset_manager,
                screen,
                text_value=c.cost,
                text_size=14,
            )
        
        # reset clipping to allow drawing everywhere again
        screen.set_clip(None)
        
        # battle button
        if len(selected) == 8: btn_battle.draw(screen)
        else: pygame.draw.rect(screen, (60, 60, 60), (btn_battle.x, btn_battle.y, btn_battle.width, btn_battle.height))
        
        pygame.display.flip()
        clock.tick(60)