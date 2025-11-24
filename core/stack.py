from core.node import Node


class Stack:
    def __init__(self):
        self.head = None

    def push(self, value):
        new_node = Node(value, self.head)
        self.head = new_node

    def pop(self):
        if not self.head:
            return None
        
        temp = self.head

        self.head = self.head.next

        return temp
        
        