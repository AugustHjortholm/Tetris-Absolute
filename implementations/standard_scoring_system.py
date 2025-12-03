"""
Standard Tetris scoring system.
Based on modern Tetris guidelines.
Values loaded from config/game_config.json
"""

from core.interfaces import IScoringSystem
from config import game_config


class StandardScoringSystem(IScoringSystem):
    """Standard Tetris scoring implementation using config values"""
    
    def __init__(self):
        self._base_scores = game_config.base_scores
        self._drop_points = game_config.drop_points
        self._speed_config = game_config.speed
    
    def calculate_score(self, lines_cleared: int, level: int, 
                       soft_drop: int = 0, hard_drop: int = 0) -> int:
        """Calculate score based on lines cleared and drop distance"""
        score = 0
        
        # Line clear scoring from config
        if lines_cleared == 1:
            score += self._base_scores["single"] * level
        elif lines_cleared == 2:
            score += self._base_scores["double"] * level
        elif lines_cleared == 3:
            score += self._base_scores["triple"] * level
        elif lines_cleared == 4:
            score += self._base_scores["tetris"] * level
        
        # Drop scoring from config
        score += soft_drop * self._drop_points["soft_drop"]
        score += hard_drop * self._drop_points["hard_drop"]
        
        return score
    
    def get_level_up_threshold(self, current_level: int) -> int:
        """Get the number of lines needed to reach the next level"""
        lines_per_level = self._speed_config["lines_per_level"]
        return current_level * lines_per_level
    
    def get_drop_speed(self, level: int) -> float:
        """Get the drop speed in seconds for a given level"""
        base_speed = self._speed_config["base_drop_interval"]
        min_speed = self._speed_config["min_drop_interval"]
        decrease = self._speed_config["speed_decrease_per_level"]
        
        speed = base_speed - (level - 1) * decrease
        return max(speed, min_speed)

