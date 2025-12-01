from core.node import Node


class Stack:
    """
    LIFO Stack implemented using a singly linked list
    """
    def __init__(self):
        self.head = None

    def is_empty(self):
        """Returns True if the stack is empty, O(1) time"""
        return self.head is None

    def push(self, value):
        """
        Pushes a value onto the top of the stack

        - Time: Worst case = Average case = O(1) inserts at head no traversal needed
        - Space: O(1) creates one new node
        
        TODO: we use this instead of array because Array push is also O(1) amortized but O(n) when resize needed; linked list is always O(1)
        """
        new_node = Node(value, self.head)
        self.head = new_node

    def pop(self):
        """
        Pops and returns the top value from the stack

        - Time: Worst case = Average case = O(1) removes from head no traversal needed
        - Space: O(1) no extra space
        
        TODO: Alternative: Array pop is also O(1); our linked list approach avoids memory fragmentation issues of array resizing
        """
        if not self.head:
            return None
        
        temp = self.head.value

        self.head = self.head.next

        return temp