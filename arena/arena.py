import random

"""
TODO: we craft only half of the arena and then mirror it to the other half.
"""


class Arena:
    """
    We are going to do all the logic in cells, the pixel management is done in the visualizer.
    """
    def __init__(self, height): # in pixels == cells? num_cells = width / cell_size
        # enforce height multiple of 16 
        if height % 16 != 0:
            raise ("height of arena needs to be a multiple of 16!!!")

        self.height_index_1 = height
        self.width_index_1 = int(height/16 * 9) # ratio of width to height

        """TODO: maybe remove"""
        self.height = height - 1 # we create this so that when we operate we don't have to remove 1 considering indexes of cells are 0 based not 1
        self.width = self.width_index_1

        print("initializing arena with sizes", self.height, self.width)


        self.height_of_river = 1 # because we are mirroring the arena this is going to be dobled

        """
        Each cell:
        - 0: empty
        - 1: grass (floor)
        - 2: bridge
        - 2: water --> we also place water where the towers are supposed to be.
        """
        # default is grass
        self.grid = [[1 for _ in range(self.width)] for _ in range(self.height)]

    def generate_river(self):
        # center is always going to be in the middle of an even number of cells, but there isn't a precise one so we handle both 
        # first center found is lower center (between the two even)

        # remember higher center is lower center + 1 
        # so we have two systems that go from lower center - (height_of_river//2) to lower center + (height_of_river//2) and from lower center + 1 - (height_of_river//2) to lower center + 1 + (height_of_river//2)
        # we combine them into one loop
        lower_center = self.height_index_1//2 - 1 
        for i in range(lower_center+1, (lower_center+1)+(self.height_of_river - 1) + 1): #  lower_center-(int(self.height_of_river//2) - 1), (lower_center+1)+(int(self.height_of_river//2) - 1) + 1)
            #print("lower center", i)
            for index in range(len(self.grid[i])):
                self.grid[i][index] = 2

    def generate_tower(self,  
        base_size_width = 3,
        base_size_height = 3,
        distance_from_left = 3,
        distance_from_bottom = 5):

        scaled_width = int(self.width_index_1/18*base_size_width)
        scaled_height = int(self.height_index_1/32*base_size_height)

        bottom_left = (int(self.width_index_1/18*distance_from_left)-1, self.height-int(self.height_index_1/32*distance_from_bottom) - 1) # from the left, from the top

        for index_row in range(bottom_left[1]-scaled_height+1, bottom_left[1]+1):
            for index_col in range(bottom_left[0], bottom_left[0]+scaled_width):
                self.grid[index_row][index_col] = 4
                print("grid", index_row, index_col)


    def generate_towers(self):
        # king tower bottom side
        # 1/32 from the bottom
        # 8/18 from the left 
        # tower is 4x4 (4/18, 4/32)
        # we are searching for bottom left corner

        base_size_width = 4
        base_size_height = 4
        distance_from_left = 8
        distance_from_bottom = 1
        self.generate_tower(base_size_width, base_size_height, distance_from_left, distance_from_bottom)


        # princes towers bottom side
        # left tower bottom left corner is
        # * 3 from the left
        # * 5 grom the bottom 
        # * size is 3x3 (3/32, 3/18)
        
        # right botttom RIGHT princess is:
        # * 5 away from the right (14/18 from the left)
        # * 5 from the bottom 
        # * size is 3x3 (3/32, 3/18)

        # princess left
        base_size_width = 3
        base_size_height = 3
        distance_from_left = 3
        distance_from_bottom = 5
        self.generate_tower(base_size_width, base_size_height, distance_from_left, distance_from_bottom)

        # princess right 
        base_size_width = 3
        base_size_height = 3
        distance_from_left = 14
        distance_from_bottom = 5
        self.generate_tower(base_size_width, base_size_height, distance_from_left, distance_from_bottom)

       
    
    def generate_path(self):
        # if passes on water create bridge
        pass

    def world_generation(self):
        self.generate_river()
        self.generate_towers()

    def draw(self):
        for row in self.grid:
            for cell in row:
                print(cell, end=" ")
            print()

if __name__ == "__main__":
    arena = Arena(1600) 
    arena.world_generation()
    arena.draw()