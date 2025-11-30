from core.node import Node
from core.stack import Stack

#class Node:
    #def __init__(self, value, next=None):
        #self.value = value # we are going to use (row, col)
        #self.next = next # ref to the parent node

def reconstruct_path(last_node: Node):
    """
    Reconstructs a path from a linked list of nodes (parent pointers) into an ordered list
    Uses a stack to reverse the traversal order

    - Time: Worst case = Average case = O(n) where n is the path length traverses the linked list once then pops all elements
    - Space: O(n) uses a stack to store all path nodes plus the output path list

    TODO: explain why we use this and not alternative: Could use recursion with O(n) call stack, but iterative with explicit stack is clearer and avoids stack overflow on long paths
    """
    stack = Stack()
    path = []
    current = last_node

    while current is not None:
        stack.push(current.value)
        current = current.next # walk back through parents and recreate a normal list from linked list

    current = stack.pop()
    while current is not None:
        path.append(current.value)
        current = stack.pop()

    return path

def append(head, value):
    """
    Appends a value to the end of a singly linked list.

    - Time: Worst case = Average case = O(n) where n is the list length must traverse to find the tail
    - Space: O(1) only creates one new node

    TODO: explain why we use this and not alternative: Maintaining a tail pointer would make this O(1); our simpler approach trades speed for memory
    """
    new_node = Node(value)
    if not head:
        return new_node

    temp_head = head
    while temp_head.next:
        temp_head = temp_head.next

    temp_head.next = new_node
    return head

def insert(head, value):
    """
    Inserts a value at the head of a singly linked list

    - Time: Worst case = Average case = O(1) directly updates head pointer
    - Space: O(1) creates one new node

    TODO: we used this instead of array insertion at index 0 because Array insertion at index 0 is O(n) due to shifting; linked list head insertion is optimal
    """
    new_node = Node(value, head)
    return new_node


if __name__ == "__main__":
    head = Node((0,0))
    node_1 = Node((0,0), head)

