
class Node:
    """
    Basic node for linked data structures, used by linked list, queue and stack
    """
    def __init__(self, value, next=None):
        self.value = value
        self.next = next