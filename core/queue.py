from core.linked_list import Node

class Queue:
    def __init__(self):
        self.head = None
        self.tail = None

    def is_empty(self):
        """Returns True if the queue is empty, O(1) time"""
        return self.head is None

    def enqueue(self, value):
        """
        Enqueues a value at the back of the queue

        - Time: Worst case = Average case = O(1) inserts at tail using tail pointer no traversal needed
        - Space: O(1) creates one new node

        TODO: we use this instead of array because Array-based enqueue is also O(1); linked list avoids fixed capacity limitations
        """
        new_node = Node(value)
        if self.head == None:
            self.head = new_node
            self.tail = new_node
        else:
            self.tail.next = new_node
            self.tail = new_node

    def dequeue(self):
        """
        Dequeues a value from the front of the queue

        - Time: Worst case = Average case = O(1) removes from head no traversal needed
        - Space: O(1) no extra space

        TODO: we use this instead of array because Array-based dequeue is O(n) for shifting elements; linked list avoids this cost
        """
        if self.head != None:
            value = self.head.value
            self.head = self.head.next
            if self.head == None:
                self.tail = None
            return value
        return None


if __name__ == "__main__":
    queue = Queue()
    queue.enqueue(1)
    queue.enqueue(2)
    queue.enqueue(3)
    print(queue.dequeue())
    print(queue.dequeue())