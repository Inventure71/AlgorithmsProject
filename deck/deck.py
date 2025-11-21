import random
from core.queue import Queue
from deck.card import Card

class Deck:
    def __init__(self, cards):
        self.full_list = cards
        self.cards = None
        self.list_to_queue(cards)

    def list_to_queue(self, cards):
        self.cards = Queue()
        for card in cards:
            self.cards.enqueue(card)

    def shuffle_cards(self):
        random.shuffle(self.full_list)
        self.list_to_queue(self.full_list)

    def get_card(self):
        #card = self.cards.dequeue()
        #self.cards.enqueue(card) # we add it back at the end so the deck can't end
        return self.cards.dequeue()
    
    def add_card(self, card): # to the end of the deck
        self.cards.enqueue(card)

        

