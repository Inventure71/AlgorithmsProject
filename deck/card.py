import math
from deck.stats import stats

class Card:
    def __init__(self, 
    name, 
    color, 
    troop_class,
    troop_name,
    asset_manager=None):
        self.name = name
        self.troop_class = troop_class
        self.color = color

        self.asset_manager = asset_manager

        self.troop_name = troop_name
        if troop_name in stats:
            self.troop_health = stats.get(troop_name).get("troop_health")
            self.troop_damage = stats.get(troop_name).get("troop_damage")
            self.troop_movement_speed = stats.get(troop_name).get("troop_movement_speed")
            self.troop_attack_type = stats.get(troop_name).get("troop_attack_type")
            self.troop_attack_speed = stats.get(troop_name).get("troop_attack_speed")
            self.troop_attack_range = stats.get(troop_name).get("troop_attack_range")
            self.troop_attack_aggro_range = stats.get(troop_name).get("troop_attack_aggro_range")
            self.troop_attack_cooldown = stats.get(troop_name).get("troop_attack_cooldown")
            self.troop_width = stats.get(troop_name).get("troop_width")
            self.troop_height = stats.get(troop_name).get("troop_height")
            self.cost = stats.get(troop_name).get("troop_cost")
            self.troop_count = stats.get(troop_name).get("troop_count")
            self.scale_multiplier = stats.get(troop_name).get("scale_multiplier")
            self.troop_type = stats.get(troop_name).get("troop_type")
            self.troop_favorite_target = stats.get(troop_name).get("troop_favorite_target")
        else:
            raise ValueError(f"Troop {troop_name} not found in stats")

    def get_card_image(self, width: int, height: int):
        """
        Get the card image scaled to specified dimensions.
        Returns None if no image is available.
        """
        if self.asset_manager:
            return self.asset_manager.get_scaled_card_image(self.troop_name, width, height)
        return None

    def create_troops(self, team):
        troops = []
        if self.troop_count is None or self.troop_count < 1:
            raise ValueError(f"Troop count for {self.troop_name} is not valid")

        for i in range(self.troop_count):
            troops.append(self.troop_class(
                name=self.troop_name, 
                health=self.troop_health, 
                damage=self.troop_damage, 
                movement_speed=self.troop_movement_speed, 
                attack_type=self.troop_attack_type, 
                attack_speed=self.troop_attack_speed, 
                attack_range=self.troop_attack_range, 
                attack_aggro_range=self.troop_attack_aggro_range,
                attack_cooldown=self.troop_attack_cooldown, 
                width=self.troop_width, 
                height=self.troop_height, 
                color=self.color, 
                team=team,
                asset_manager=self.asset_manager,
                scale_multiplier=self.scale_multiplier,
                troop_type=self.troop_type,
                troop_favorite_target=self.troop_favorite_target)
            )
        return troops

    def get_formation_positions(self, location, troop_count, enforce_valid=False, arena=None, team=None):
        # we want to do rows of sqrt(troop_count)
        
        rows = int(math.sqrt(troop_count))
        cols = int(math.ceil(troop_count / rows))
        # for 1x1 troops, spacing is 1
        # for larger troops, use their size
        row_spacing = max(1, self.troop_height)
        col_spacing = max(1, self.troop_width)

        # calculate the center position of the formation
        center_row, center_col = location
        total_height = (rows - 1) * row_spacing + self.troop_height
        total_width = (cols - 1) * col_spacing + self.troop_width
        start_row = center_row - (total_height // 2)
        start_col = center_col - (total_width // 2)

        positions = []
        troop_index = 0

        positions = []
        for row in range(rows):
            for col in range(cols):
                if troop_index >= troop_count:
                    break

                pos_row = start_row + (row * row_spacing)
                pos_col = start_col + (col * col_spacing)
                position = (pos_row, pos_col)

                if enforce_valid: # this means that we check here if all cells this troop would occupy are valid
                    if not self._is_formation_position_valid(position, arena, team):
                        return []
                
                positions.append(position)
                troop_index += 1

        return positions

    def _is_formation_position_valid(self, position, arena, team):
        """Check if a single troop position is valid (all cells it occupies must be placable)"""
        if not arena:
            return True
        
        base_row, base_col = position
        for row in range(base_row, base_row + self.troop_height):
            for col in range(base_col, base_col + self.troop_width):
                if not arena.is_placable_cell(row, col, team):
                    return False
        return True