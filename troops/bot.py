class GreedyBot:
    """
    Greedy bot that makes locally optimal choices for card and position selection
    Uses heuristic scoring to evaluate threats and find counters
    """
    
    def __init__(self, player, arena):
        self.player = player
        self.arena = arena
        self.cooldown = 0
        self.min_elixir = 4
        self.counters = {
            "air": ["archer", "musketeer", "dart goblin", "bats", "spear goblin"],
            "tank": ["mini pekka", "pekka", "elite barbs", "barbarian"],
            "swarm": ["archer", "musketeer", "dart goblin"],
            "building_targeter": ["goblins", "skeletons", "knight", "barbarian"],
        }
    
    def think(self):
        """
        Main decision: returns (card, position) or (None, None)
        Greedy approach: react to threats first, otherwise play offensively
        """
        if self.cooldown > 0:
            self.cooldown -= 1
            return None, None
        
        if self.player.current_elixir < self.min_elixir:
            return None, None
        
        threat = self._find_threat()
        
        if threat:
            card = self._find_counter(threat)
            pos = self._best_position(card, threat, defensive=True)
        else:
            card = self._find_offensive_card()
            pos = self._best_position(card, None, defensive=False)
        
        if card and pos:
            self.cooldown = 60
            return card, pos
        
        return None, None
    
    def _get_positions(self):
        """Returns strategic positions based on team side"""
        h = self.arena.height
        w = self.arena.width
        mid_h = h // 2
        mid_w = w // 2
        
        if self.player.team == 2:
            return [
                (3, mid_w), (4, 3), (4, w - 4),
                (mid_h - 3, 3), (mid_h - 3, w - 4),
                (mid_h // 2, mid_w), (8, 4), (8, w - 5),
            ]
        else:
            return [
                (h - 4, mid_w), (h - 5, 3), (h - 5, w - 4),
                (mid_h + 3, 3), (mid_h + 3, w - 4),
                (h - mid_h // 2, mid_w), (h - 9, 4), (h - 9, w - 5),
            ]
    
    def _score_position(self, pos, card, threat, defensive):
        """Scores a position using weighted heuristics, higher is better"""
        row, col = pos
        is_flying = getattr(card, 'troop_can_fly', False) if card else False
        
        if not self.arena.is_placable_cell(row, col, self.player.team, is_flying=is_flying):
            return float('-inf')
        
        score = 0
        
        if defensive and threat:
            t_row, t_col = threat.location
            dist_to_threat = abs(row - t_row) + abs(col - t_col)
            score += max(0, 30 - dist_to_threat * 2)
            
            if abs(col - t_col) <= 3:
                score += 15
            
            # bonus for being between threat and our tower
            if self.player.team == 2 and row > t_row:
                score += 20
            elif self.player.team != 2 and row < t_row:
                score += 20
            
            if self._dist_to_tower(pos, own=True) > 5:
                score += 10
        else:
            dist_to_enemy = self._dist_to_tower(pos, own=False)
            score += max(0, 25 - dist_to_enemy)
            
            # safe back position bonus
            if self.player.team == 2 and row < 6:
                score += 20
            elif self.player.team != 2 and row > self.arena.height - 7:
                score += 20
            
            lane_count = self._lane_troops(col)
            if lane_count == 0:
                score += 15
            elif lane_count == 1:
                score += 8
            
            # building targeters prefer center
            if card and getattr(card, 'troop_favorite_target', None) == "building":
                if abs(col - self.arena.width // 2) <= 2:
                    score += 10
        
        return score
    
    def _best_position(self, card, threat, defensive):
        """Finds highest scoring position using greedy selection"""
        best_pos = None
        best_score = float('-inf')
        
        for pos in self._get_positions():
            score = self._score_position(pos, card, threat, defensive)
            if score > best_score:
                best_score = score
                best_pos = pos
        
        if best_pos and best_score > float('-inf'):
            return best_pos
        
        # fallback: positions near threat
        if threat and hasattr(threat, 'location') and threat.location:
            t_row, t_col = threat.location
            for r_off, c_off in [(2, 0), (-2, 0), (0, 2), (0, -2)]:
                test_row = t_row + abs(r_off) if self.player.team == 2 else t_row - abs(r_off)
                test_col = t_col + c_off
                if self.arena.is_placable_cell(test_row, test_col, self.player.team, is_flying=False):
                    return (test_row, test_col)
        
        # last resort: any valid cell
        return self._find_any_valid_position()
    
    def _find_any_valid_position(self):
        """Finds any valid placement position as fallback"""
        mid_h = self.arena.height // 2
        
        if self.player.team == 2:
            row_range = range(3, mid_h - 2)
        else:
            row_range = range(mid_h + 2, self.arena.height - 3)
        
        for row in row_range:
            for col in range(2, self.arena.width - 2):
                if self.arena.is_placable_cell(row, col, self.player.team, is_flying=False):
                    return (row, col)
        return None
    
    def _dist_to_tower(self, pos, own=True):
        """Computes Manhattan distance to nearest tower"""
        if isinstance(pos, tuple):
            row, col = pos
        elif hasattr(pos, 'location') and pos.location:
            row, col = pos.location
        else:
            return float('inf')
        
        if own:
            towers = self.arena.towers_P2 if self.player.team == 2 else self.arena.towers_P1
        else:
            towers = self.arena.towers_P1 if self.player.team == 2 else self.arena.towers_P2
        
        if not towers:
            return float('inf')
        
        min_dist = float('inf')
        for tower in towers.values():
            if not tower.is_alive or not hasattr(tower, 'location') or not tower.location:
                continue
            t_row, t_col = tower.location
            dist = abs(row - t_row) + abs(col - t_col)
            if dist < min_dist:
                min_dist = dist
        
        return min_dist if min_dist != float('inf') else 1
    
    def _lane_troops(self, col):
        """Counts friendly troops in the same lane"""
        mid_w = self.arena.width // 2
        is_left_lane = col < mid_w
        count = 0
        
        for troop in self.arena.unique_troops:
            if troop.team != self.player.team or not troop.is_alive:
                continue
            if not hasattr(troop, 'location') or not troop.location:
                continue
            if (troop.location[1] < mid_w) == is_left_lane:
                count += 1
        
        return count
    
    def _find_threat(self):
        """Finds highest threat: damage / distance to our tower"""
        best_threat = None
        best_score = 0
        
        for troop in self.arena.unique_troops:
            if troop.team == self.player.team or not troop.is_alive:
                continue
            if getattr(troop, 'troop_type', '') == "building":
                continue
            
            dist = self._dist_to_tower(troop, own=True)
            if dist <= 0:
                continue
            
            threat_score = troop.damage / dist
            if threat_score > best_score:
                best_score = threat_score
                best_threat = troop
        
        return best_threat
    
    def _categorize_threat(self, threat):
        """Categorizes threat for counter selection"""
        if threat.troop_can_fly:
            return "air"
        if threat.health > 1500:
            return "tank"
        if getattr(threat, 'troop_favorite_target', '') == "building":
            return "building_targeter"
        return "swarm"
    
    def _find_counter(self, threat):
        """Finds best counter card using greedy matching"""
        affordable = [c for c in self.player.hand if c.cost <= self.player.current_elixir]
        if not affordable:
            return None
        
        threat_type = self._categorize_threat(threat)
        counter_names = self.counters.get(threat_type, [])
        
        for card in affordable:
            if card.troop_name in counter_names:
                return card
        
        # fallback: cheapest card
        return min(affordable, key=lambda c: c.cost)
    
    def _find_offensive_card(self):
        """Finds best offensive card: building targeters or highest HP"""
        affordable = [c for c in self.player.hand if c.cost <= self.player.current_elixir]
        if not affordable:
            return None
        
        # prefer building targeters
        for card in affordable:
            if getattr(card, 'troop_favorite_target', None) == "building":
                return card
        
        # otherwise highest HP value
        return max(affordable, key=lambda c: getattr(c, 'troop_health', 100) * getattr(c, 'troop_count', 1))