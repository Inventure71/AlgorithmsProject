from collections import deque
from arena.utils.random_utils import is_walkable
from arena.utils.random_utils import is_cell_in_bounds
from core.linked_list import reconstruct_path
from core.node import Node

# we modified this function to take into account the width of the troop so that we can check if the path is valid for the troop if it isn't 1 sized
def get_valid_neighbors(cell: (int, int), grid, collision_grid, self_troop, include_non_walkable=False, include_diagonals=False):
    """
    Gets valid neighboring cells for pathfinding, accounting for troop size

    - Time: Worst case = Average case = O(d * tw * th) where d is directions 4 or 8 and tw/th are troop dimensions
    - Space: O(d)

    TODO: is the alternative better? Alternative: Could use DFS for neighbor finding; BFS exploration is more systematic for grid-based movement
    """
    if include_diagonals:
        # these are the 4 directions --> up, down, left, right, top_right, bottom_right, top_right, bottom_left
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1,1), (-1,1), (1,-1)]
    else:
        # these are the 4 directions --> up, down, left, right
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    
    neighbors = []

    for direction in directions:
        row = cell[0] + direction[0]
        col = cell[1] + direction[1]

        all_cells_valid = True
        for r in range(row, row + self_troop.height):
            for c in range(col, col + self_troop.width):
                if not is_cell_in_bounds((r, c), grid):
                    all_cells_valid = False
                    break
                if not is_walkable(r, c, grid, is_flying=self_troop.troop_can_fly):
                    all_cells_valid = False
                    break
                if ((r, c) in collision_grid and collision_grid[(r, c)] != self_troop):
                    all_cells_valid = False
                    break

        # we need the include_non_walkable to find path that is 1 away to something unwalkable, es towers
        if all_cells_valid:
            neighbors.append((row, col, True)) # (row, col, is valid cell to walk on)
            
        elif include_non_walkable:
            if is_cell_in_bounds((row, col), grid):
                neighbors.append((row, col, False)) 

    return neighbors


def find_path_bfs(start, grid, collision_grid, target_grid, self_troop, goal_cell=None, cell_type=None, one_tile_range=True, include_diagonals=True): # one tile range means we are going to check for adiencent impossible to reach points
    """
    BFS pathfinding to find shortest path to goal or nearest cell of type

    collision_grid: Used for obstacle avoidance (based on moving troop's type)
    target_grid: Used for finding the target (based on target's type)
    goal_cell = the specific (row, col) of the cell we want to find
    cell_type = find closest cell of this type and the path to it

    - Time: Worst case = Average case = O(V + E) where V is vertices h*w grid cells and E is edges up to 8*V for 8 directional
    - Space: O(V) for visited set and queue may visit all cells in worst case
    
    This implementation is better than a DFS because it guarantees the shortest path
    """
    if cell_type and goal_cell: # xor opearor 
        raise ValueError("Either cell_type or goal_cell need to have a value, not both")
    if not cell_type and not goal_cell:
        raise ValueError("Either cell_type or goal_cell need to have a value, neither is set")

    # queue holds tuples: (current_tile, path_list)
    # we start at 'start', and the path contains just ['start']

    start_node = Node(start, None)
    queue = deque([start_node])

    # we keep track of seen tiles to not incur in loops
    visited = set()
    visited.add(start)

    # while our list isn't empty
    while queue:
        # get the first node from queue
        current_node = queue.popleft()
        curr_row, curr_col = current_node.value

        if cell_type and grid[curr_row][curr_col] == cell_type:
            # found the cell type that we wanted (edge case: if we somehow start on the target cell type)
            return reconstruct_path(current_node)
        elif goal_cell and (curr_row, curr_col) == goal_cell:
            # found the specific cell that we wanted
            return reconstruct_path(current_node)
        
        if (curr_row, curr_col) in target_grid and target_grid[(curr_row, curr_col)] == cell_type:
            return reconstruct_path(current_node)
        
        neighbors = get_valid_neighbors((curr_row, curr_col), grid, collision_grid, self_troop, include_non_walkable=one_tile_range, include_diagonals=include_diagonals)

        # we loop each neighbor
        for neighbor in neighbors:
            is_valid = neighbor[2]
            neighbor = (neighbor[0], neighbor[1])

            # if it is in visited then we skip it
            if not (neighbor in visited):
                
                if one_tile_range:
                    if (cell_type and grid[neighbor[0]][neighbor[1]] == cell_type):
                        return reconstruct_path(Node(neighbor, current_node))
                    if goal_cell and (neighbor[0], neighbor[1]) == goal_cell:
                        return reconstruct_path(Node(neighbor, current_node))

                    if neighbor in target_grid and target_grid[neighbor] == cell_type:
                        return reconstruct_path(Node(neighbor, current_node))
                
                # so that we don't visit it in the future
                if is_valid:
                    visited.add(neighbor)
                    queue.append(Node(neighbor, current_node))

    return None # meaning couldn't find any path
            