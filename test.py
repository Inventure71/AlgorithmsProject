from deck.card import Card
from deck.deck import Deck

if __name__ == "__main__":
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
    print(deck.get_card().name)
    print(deck.get_card().name)

    print("next 2 cards in deck:")
    print(deck.cards.head.value.name)
    print(deck.cards.head.next.value.name)

    print("Shuffling cards")
    deck.shuffle_cards()

    print("next 2 cards in deck:")
    print(deck.get_card().name)
    print(deck.get_card().name)