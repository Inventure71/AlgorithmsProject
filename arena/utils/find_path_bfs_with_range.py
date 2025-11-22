from collections import deque
from arena.utils.random_utils import is_walkable

def get_valid_neighbors(cell: (int, int), grid, occupancy_grid, include_diagonals=False):
    """
    Returns only strictly walkable neighbors for pathing purposes.
    The check for 'reaching' a non-walkable target is now handled in the main BFS loop via range.
    """
    if include_diagonals:
        # 8 directions
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, 1), (-1, 1), (1, -1)]
    else:
        # 4 directions
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    
    neighbors = []

    for direction in directions:
        row = cell[0] + direction[0]
        col = cell[1] + direction[1]
        
        # Check bounds
        if 0 <= row < len(grid) and 0 <= col < len(grid[0]):
            # Strictly check walkability for movement
            if is_walkable(row, col, grid) and (row, col) not in occupancy_grid:
                neighbors.append((row, col))

    return neighbors

def get_distance(p1, p2, use_diagonals):
    """
    Calculates distance between two points.
    - Chebyshev (Max of dx, dy) if diagonals are allowed (standard for grid range).
    - Manhattan (dx + dy) if diagonals are not allowed.
    """
    dx = abs(p1[0] - p2[0])
    dy = abs(p1[1] - p2[1])
    if use_diagonals:
        return max(dx, dy)
    return dx + dy

def is_target_in_range(current_cell, grid, goal_cell, cell_type, action_range, include_diagonals):
    """
    Checks if the goal is within 'action_range' of 'current_cell'.
    """
    # 1. Case: Specific Goal Cell
    if goal_cell:
        dist = get_distance(current_cell, goal_cell, include_diagonals)
        return dist <= action_range

    # 2. Case: Specific Cell Type (Scan surroundings)
    elif cell_type:
        # We optimize by defining the bounding box of the range to avoid checking the whole grid
        rows = len(grid)
        cols = len(grid[0])
        
        r_min = max(0, current_cell[0] - action_range)
        r_max = min(rows - 1, current_cell[0] + action_range)
        c_min = max(0, current_cell[1] - action_range)
        c_max = min(cols - 1, current_cell[1] + action_range)

        for r in range(r_min, r_max + 1):
            for c in range(c_min, c_max + 1):
                # Check if this cell is the type we want
                if grid[r][c] == cell_type:
                    # Verify exact distance (needed because bounding box is square, 
                    # but Manhattan distance creates a diamond shape)
                    if get_distance(current_cell, (r, c), include_diagonals) <= action_range:
                        return True
    return False

def find_path_bfs_w_range(start, grid, occupancy_grid, goal_cell=None, cell_type=None, action_range=6, include_diagonals=True): 
    """
    action_range: The allowed distance (in tiles) from the target to consider the path complete.
                  e.g., 5 means we stop when we are <= 5 tiles away.
    """
    if cell_type and goal_cell: 
        raise ValueError("Either cell_type or goal_cell need to have a value, not both")
    if not cell_type and not goal_cell:
        raise ValueError("Either cell_type or goal_cell need to have a value, neither is set")

    # queue holds tuples: (current_tile, path_list)
    queue = deque([(start, [start])])

    # we keep track of seen tiles to not incur in loops
    visited = set()
    visited.add(start)

    while queue:
        current_node, path = queue.popleft()

        # CHECK: Are we within N range of the target?
        # We check this immediately. If we start in range, we return immediately.
        if is_target_in_range(current_node, grid, goal_cell, cell_type, action_range, include_diagonals):
            return path
        
        # Get neighbors
        neighbors = get_valid_neighbors(current_node, grid, occupancy_grid, include_diagonals=include_diagonals)

        for neighbor in neighbors:
            if neighbor not in visited:
                visited.add(neighbor)
                new_path = path + [neighbor]
                queue.append((neighbor, new_path))

    return None # meaning couldn't find any path