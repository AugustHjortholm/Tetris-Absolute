"""
Standard Tetris scoring system.
Based on modern Tetris guidelines.
"""

from core.interfaces import IScoringSystem


class StandardScoringSystem(IScoringSystem):
    """Standard Tetris scoring implementation"""
    
    def calculate_score(self, lines_cleared: int, level: int, 
                       soft_drop: int = 0, hard_drop: int = 0) -> int:
        """Calculate score based on lines cleared and drop distance"""
        score = 0
        
        # Line clear scoring (modern Tetris scoring)
        if lines_cleared == 1:
            score += 100 * level
        elif lines_cleared == 2:
            score += 300 * level
        elif lines_cleared == 3:
            score += 500 * level
        elif lines_cleared == 4:
            score += 800 * level  # Tetris!
        
        # Drop scoring
        score += soft_drop  # 1 point per cell for soft drop
        score += hard_drop * 2  # 2 points per cell for hard drop
        
        return score
    
    def get_level_up_threshold(self, current_level: int) -> int:
        """Get the number of lines needed to reach the next level"""
        # Level up every 10 lines
        return current_level * 10
    
    def get_drop_speed(self, level: int) -> float:
        """Get the drop speed in seconds for a given level"""
        # Gets faster as level increases
        base_speed = 1.0  # 1 second at level 1
        min_speed = 0.1   # Minimum 0.1 seconds
        
        speed = base_speed - (level - 1) * 0.05
        return max(speed, min_speed)

