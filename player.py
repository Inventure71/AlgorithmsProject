from core.linear_search import linear_search

class Player:
    """
    Represents a player with deck, hand, and elixir management
    """
    def __init__(self, name, deck, team, arena, max_elixir=10.0):
        self.name = name
        self.deck = deck
        self.team = team

        self.arena = arena

        self.max_hand_size = 4
        self.hand = []

        # this is going to be a float
        self.current_elixir = max_elixir//2 # we start with half like in the real game
        self.max_elixir = max_elixir

        # at base rate it's 1 Elixir every 2.8 seconds, which equals to 0.06 every tick
        self.elixir_per_tick = 0.006 # every tick, with a bit of eccess (0,008) but it is fine in this case
    
    def increase_elixir(self):
        """
        Increases elixir by tick rate with multiplier
        
        - Time: O(1) simple arithmetic
        - Space: O(1) no allocations
        """
        if self.current_elixir + (self.elixir_per_tick* self.arena.elixir_multiplier) <= self.max_elixir: # parenthesis not needed but better to read
            self.current_elixir += self.elixir_per_tick * self.arena.elixir_multiplier
        else:
            self.current_elixir = self.max_elixir

    def place_troop(self, location, card):
        """
        Places troops from a card at specified location and draws replacement card

        - Time: Worst case = Average case = O(c * tw * th + h) where:
            - c is troop count (from card)
            - tw/th are troop width/height for spawn validation
            - h is hand size (4) for linear search
        - Space: O(c) for troops list

        NOTE: Uses swap-in-place via draw_card(swap=index) to achieve O(1) card replacement instead of O(h) removal + O(1) append. 
        NOTE: Linear search O(h) is unavoidable for finding the card, but h is constant (4) so effectively O(1).
        """
        #troop = card.create_troop(self.team)
        troops = card.create_troops(self.team)
        cost = card.cost
        if cost > self.current_elixir:
            # not enough elixir
            return False

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

        self.current_elixir = self.current_elixir - cost
        # use my custom linear search to find the card index
        index = linear_search(self.hand, card)
        if index != -1:
            # we don't need to remove the card by index, we need to swap it with the drawn card
            self.draw_card(swap=index) # we subsitute in place
    
        self.deck.add_card(card) 
        # we don't even need to call the draw card function because we already drew a card
        return True

    def draw_card(self, swap=None):
        """
        Draws a card from deck to hand, either appending or swapping in place if a swap index is provided

        - Time: Worst case = Average case = O(1)
            - Queue dequeue is O(1) with tail pointer
            - List index assignment is O(1)
            - List append is O(1) amortized
        - Space: O(1) adds one card reference

        The swap parameter enables O(1) in-place replacement instead of O(h) pop + O(1) append when replacing a played card.
        """
        if swap is not None:
            self.hand[swap] = self.deck.get_card()
            return True
        else:
            if len(self.hand) < self.max_hand_size:
                self.hand.append(self.deck.get_card())
                return True
            return False

    def setup_hand(self):
        """
        Fills hand to max capacity at game start

        - Time: Worst case = Average case = O(h) where h is max_hand_size (4) draws h cards
        - Space: O(h) for hand list
        """
        while len(self.hand) < self.max_hand_size:
            self.draw_card()
        return True