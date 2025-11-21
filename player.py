from arena import arena
from core.linear_search import linear_search

class Player:
    def __init__(self, name, deck, team, arena):
        self.name = name
        self.deck = deck
        self.team = team

        self.arena = arena

        self.max_hand_size = 4
        self.hand = []

    def place_troop(self, location, card):
        troop = card.create_troop(self.team)
        self.arena.spawn_unit(troop, location)

        # use my custom linear search to find the card index
        index = linear_search(self.hand, card)
        if index != -1:
            # remove the card by index
            self.hand.pop(index)
        self.deck.add_card(card)
        self.draw_card()

    def draw_card(self):
        if len(self.hand) < self.max_hand_size:
            self.hand.append(self.deck.get_card())
            return True
        return False

    def setup_hand(self):
        while len(self.hand) < self.max_hand_size:
            self.draw_card()
        return True