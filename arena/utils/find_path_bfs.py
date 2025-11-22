from collections import deque
from arena.utils.random_utils import is_walkable

def get_valid_neighbors(cell: (int, int), grid, occupancy_grid, include_non_walkable=False):
    # these are the 4 directions --> up, down, left, right
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    neighbors = []

    for direction in directions:
        row = cell[0] + direction[0]
        col = cell[1] + direction[1]
        
        # we need the include_non_walkable to find path that is 1 away to something unwalkable, es towers
        if 0 <= row < len(grid) and 0 <= col < len(grid[0]):
            if is_walkable(row, col, grid) and (row, col) not in occupancy_grid:
                neighbors.append((row, col, True)) # (row, col, is valid cell to walk on)
            elif include_non_walkable:
                neighbors.append((row, col, False)) 
    return neighbors


def find_path_bfs(start, grid, occupancy_grid, goal_cell=None, cell_type=None, one_tile_range=True): # one tile range means we are going to check for adiencent impossible to reach points 
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

        if cell_type and grid[current_node[0]][current_node[1]] == cell_type:
            # found the cell type that we wanted (edge case: if we somehow start on the target cell type)
            return path
        elif goal_cell and (current_node[0], current_node[1]) == goal_cell:
            # found the specific cell that we wanted
            return path
        
        neighbors = get_valid_neighbors(current_node, grid, occupancy_grid, include_non_walkable=one_tile_range)

        # we loop each neighbor
        for neighbor in neighbors:
            is_valid = neighbor[2]
            neighbor = (neighbor[0], neighbor[1])

            # if it is in visited then we skip it
            if not (neighbor in visited):
                
                if one_tile_range:
                    if (cell_type and grid[neighbor[0]][neighbor[1]] == cell_type):
                        return path
                    if goal_cell and (neighbor[0], neighbor[1]) == goal_cell:
                        return path
                
                # so that we don't visit it in the future
                if is_valid:
                    visited.add(neighbor)

                    # this path will include the old path and the neighbor
                    new_path = path + [neighbor]

                    queue.append((neighbor, new_path))

    return None # meaning couldn't find any path
            