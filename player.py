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
        #troop = card.create_troop(self.team)
        troops = card.create_troops(self.team)

        if len(troops) == 1:
            print(f"Spawning {troops[0].name} at {location}")
            if not self.arena.spawn_unit(troops[0], location):
                return False
        else:
            print(f"Spawning {len(troops)} troops at {location}")
            formation_positions = card.get_formation_positions(location, len(troops), enforce_valid=True, arena=self.arena, team=self.team)

            if len(formation_positions) == 0:
                print(f"No valid formation positions for {card.name}")
                return False
            
            for index, position in enumerate(formation_positions):
                if not self.arena.spawn_unit(troops[index], position):
                    print("Strange failure spawning troops")
                    return False

        # use my custom linear search to find the card index
        index = linear_search(self.hand, card)
        if index != -1:
            # remove the card by index
            self.hand.pop(index)
        self.deck.add_card(card)
        self.draw_card()
        return True

    def draw_card(self):
        if len(self.hand) < self.max_hand_size:
            self.hand.append(self.deck.get_card())
            return True
        return False

    def setup_hand(self):
        while len(self.hand) < self.max_hand_size:
            self.draw_card()
        return True