from core.node import Node
from core.stack import Stack

#class Node:
    #def __init__(self, value, next=None):
        #self.value = value # we are going to use (row, col)
        #self.next = next # ref to the parent node

def reconstruct_path(last_node: Node):
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
    new_node = Node(value)
    if not head:
        return new_node

    temp_head = head
    while temp_head.next:
        temp_head = temp_head.next

    temp_head.next = new_node
    return head

def insert(head, value):
    new_node = Node(value, head)
    return new_node


if __name__ == "__main__":
    head = Node((0,0))
    node_1 = Node((0,0), head)

