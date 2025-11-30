import random
from core.queue import Queue
from deck.card import Card

class Deck:
    """
    Manages a deck of cards using a queue for draw order
    """
    def __init__(self, cards):
        self.full_list = cards
        self.cards = None
        self.list_to_queue(cards)

    def list_to_queue(self, cards):
        """
        Converts a list of cards to a queue

        - Time: Worst case O(n), Average case O(n) where n is cards enqueues each card
        - Space: O(n) for queue nodes
        """
        self.cards = Queue()
        for card in cards:
            self.cards.enqueue(card)

    def shuffle_cards(self):
        """
        Shuffles deck using Fisher-Yates shuffle (via random.shuffle)

        - Time: Worst case = Average case = O(n) for shuffle plus O(n) for queue rebuild equals O(n)
        - Space: O(n) for new queue
        """
        # TODO: maybe implement this in core 
        random.shuffle(self.full_list)
        self.list_to_queue(self.full_list)

    def get_card(self):
        """
        Draws a card from the deck
        
        - Time: Worst case = Average case = O(1) dequeue from linked list queue
        - Space: O(1) no additional allocation
        """
        return self.cards.dequeue()
    
    def add_card(self, card): # to the end of the deck
        """
        Adds a card to the back of the deck

        - Time: Worst case = Average case = O(1) enqueue to linked list queue with tail pointer
        - Space: O(1) one new node

        TODO: we use this because array append could require resize O(n); linked list queue is always O(1)
        """
        self.cards.enqueue(card)

        

