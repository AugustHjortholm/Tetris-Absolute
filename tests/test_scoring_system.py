"""
Unit tests for Scoring System implementation.
Tests score calculation and level progression.
"""

import pytest
from implementations.standard_scoring_system import StandardScoringSystem


class TestStandardScoringSystem:
    """Test the StandardScoringSystem"""
    
    def test_single_line_clear(self):
        """Test scoring for single line clear"""
        scoring = StandardScoringSystem()
        
        score = scoring.calculate_score(lines_cleared=1, level=1)
        assert score == 100
        
        # Higher level = more points
        score = scoring.calculate_score(lines_cleared=1, level=5)
        assert score == 500
    
    def test_double_line_clear(self):
        """Test scoring for double line clear"""
        scoring = StandardScoringSystem()
        
        score = scoring.calculate_score(lines_cleared=2, level=1)
        assert score == 300
        
        score = scoring.calculate_score(lines_cleared=2, level=3)
        assert score == 900
    
    def test_triple_line_clear(self):
        """Test scoring for triple line clear"""
        scoring = StandardScoringSystem()
        
        score = scoring.calculate_score(lines_cleared=3, level=1)
        assert score == 500
    
    def test_tetris_line_clear(self):
        """Test scoring for Tetris (4 lines)"""
        scoring = StandardScoringSystem()
        
        score = scoring.calculate_score(lines_cleared=4, level=1)
        assert score == 800
        
        score = scoring.calculate_score(lines_cleared=4, level=10)
        assert score == 8000
    
    def test_soft_drop_points(self):
        """Test soft drop adds points"""
        scoring = StandardScoringSystem()
        
        score = scoring.calculate_score(
            lines_cleared=0, 
            level=1, 
            soft_drop=10
        )
        assert score == 10
    
    def test_hard_drop_points(self):
        """Test hard drop adds points (2x soft drop)"""
        scoring = StandardScoringSystem()
        
        score = scoring.calculate_score(
            lines_cleared=0, 
            level=1, 
            hard_drop=10
        )
        assert score == 20
    
    def test_combined_scoring(self):
        """Test combining line clear and drop points"""
        scoring = StandardScoringSystem()
        
        # Single line + hard drop from 5 cells
        score = scoring.calculate_score(
            lines_cleared=1,
            level=1,
            hard_drop=5
        )
        assert score == 100 + 10  # 100 for line + 10 for drop
    
    def test_level_up_threshold(self):
        """Test level up thresholds"""
        scoring = StandardScoringSystem()
        
        assert scoring.get_level_up_threshold(1) == 10
        assert scoring.get_level_up_threshold(2) == 20
        assert scoring.get_level_up_threshold(5) == 50
    
    def test_drop_speed_decreases(self):
        """Test drop speed gets faster with level"""
        scoring = StandardScoringSystem()
        
        speed_1 = scoring.get_drop_speed(1)
        speed_5 = scoring.get_drop_speed(5)
        speed_10 = scoring.get_drop_speed(10)
        
        # Higher level = faster (lower time)
        assert speed_5 < speed_1
        assert speed_10 < speed_5
    
    def test_drop_speed_minimum(self):
        """Test drop speed has a minimum"""
        scoring = StandardScoringSystem()
        
        # Very high level shouldn't go below minimum
        speed = scoring.get_drop_speed(100)
        assert speed >= 0.1  # Minimum is 0.1 seconds
    
    def test_no_lines_no_score(self):
        """Test no score for no lines cleared"""
        scoring = StandardScoringSystem()
        
        score = scoring.calculate_score(lines_cleared=0, level=1)
        assert score == 0

