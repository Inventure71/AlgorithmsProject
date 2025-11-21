from collections import deque
from operator import xor

def get_valid_neighbors(cell: (int, int), arena):
    # these are the 4 directions --> up, down, left, right
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    neighbors = []

    for direction in directions:
        row = cell[0] + direction[0]
        col = cell[1] + direction[1]

        if 0 <= row < arena.height and 0 <= col < arena.width:
            if arena.is_walkable(row, col):
                neighbors.append((row, col))

    return neighbors

def find_path_bfs(start, arena, goal_cell=None, cell_type=None):
    """
    goal_cell = the specific (row, col) of the cell we want to find 
    cell_type = find closest cell of this type and the path to it
    """
    if cell_type and goal_cell: # xor opearor 
        raise ValueError("Either cell_type or goal_cell need to have a value, not both")
    if not cell_type and not goal_cell:
        raise ValueError("Either cell_type or goal_cell need to have a value, neither is set")

    # queue holds tuples: (current_tile, path_list)
    # we start at 'start', and the path contains just ['start']
    queue = deque([(start, [start])])

    # we keep track of seen tiles to not incur in loops
    visited = set()
    visited.add(start)

    # while our list isn't empty
    while queue:
        # get the first node from queue
        current_node, path = queue.popleft()

        if cell_type and arena.grid[current_node[0]][current_node[1]] == cell_type:
            # found the cell type that we wanted
            return path
    
        elif not cell_type and current_node == goal_cell:
            # found the specific cell that we wanted
            return path
        
        neighbors = get_valid_neighbors(current_node, arena)

        # we loop each neighbor
        for neighbor in neighbors:

            # if it is in visited then we skip it
            if not (neighbor in visited):

                # so that we don't visit it in the future
                visited.add(neighbor)

                # this path will include the old path and the neighbor
                new_path = path + [neighbor]

                queue.append((neighbor, new_path))

    return None # meaning couldn't find any path
            