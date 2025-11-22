from constants import *

def is_walkable(row, col, grid):
        return grid[row][col] in walkable_cells


def is_cell_in_bounds(cell: (int, int), grid):
    if not (cell[0] >= 0 and cell[0] < len(grid)):
        return False

    if not (cell[1] >= 0 and cell[1] < len(grid[0])):
        return False

    return True