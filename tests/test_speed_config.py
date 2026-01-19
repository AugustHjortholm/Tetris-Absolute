"""
Tests for speed configuration and drop mechanics.
"""

import pytest
from config import game_config
from implementations.standard_scoring_system import StandardScoringSystem


class TestSpeedConfig:
    """Tests for speed configuration values"""
    
    def test_base_drop_interval(self):
        """Test base drop interval is 1 second"""
        assert game_config.speed["base_drop_interval"] == 1.0
    
    def test_min_drop_interval(self):
        """Test minimum drop interval is 0.1 seconds"""
        assert game_config.speed["min_drop_interval"] == 0.1
    
    def test_speed_decrease_per_level(self):
        """Test speed decreases by 0.05 per level"""
        assert game_config.speed["speed_decrease_per_level"] == 0.05
    
    def test_soft_drop_multiplier(self):
        """Test soft drop is 10x faster"""
        assert game_config.speed["soft_drop_multiplier"] == 10.0
    
    def test_lines_per_level(self):
        """Test 10 lines per level"""
        assert game_config.speed["lines_per_level"] == 10


class TestDropSpeedCalculation:
    """Tests for drop speed calculations using scoring system"""
    
    def setup_method(self):
        """Setup scoring system for each test"""
        self.scoring = StandardScoringSystem()
    
    def test_level_1_speed(self):
        """Test level 1 drop speed"""
        speed = self.scoring.get_drop_speed(1)
        assert speed == 1.0
    
    def test_level_5_speed(self):
        """Test level 5 drop speed"""
        speed = self.scoring.get_drop_speed(5)
        expected = 1.0 - (5 - 1) * 0.05  # 0.8
        assert speed == expected
    
    def test_level_10_speed(self):
        """Test level 10 drop speed"""
        speed = self.scoring.get_drop_speed(10)
        expected = 1.0 - (10 - 1) * 0.05  # 0.55
        assert speed == expected
    
    def test_speed_has_minimum(self):
        """Test that speed doesn't go below minimum"""
        speed = self.scoring.get_drop_speed(100)
        min_speed = game_config.speed["min_drop_interval"]
        assert speed >= min_speed
        assert speed == min_speed
    
    def test_soft_drop_speed(self):
        """Test soft drop speed calculation"""
        base_speed = self.scoring.get_drop_speed(1)
        soft_mult = game_config.speed["soft_drop_multiplier"]
        soft_speed = base_speed / soft_mult
        assert soft_speed == 0.1  # 1.0 / 10


class TestLevelProgression:
    """Tests for level progression configuration"""
    
    def setup_method(self):
        """Setup scoring system for each test"""
        self.scoring = StandardScoringSystem()
    
    def test_level_1_threshold(self):
        """Test lines needed for level 2"""
        threshold = self.scoring.get_level_up_threshold(1)
        lines_per_level = game_config.speed["lines_per_level"]
        assert threshold == lines_per_level  # 10 lines
    
    def test_level_5_threshold(self):
        """Test lines needed at level 5"""
        threshold = self.scoring.get_level_up_threshold(5)
        assert threshold == 50  # 5 * 10
    
    def test_threshold_scales_with_level(self):
        """Test that threshold scales linearly"""
        for level in range(1, 20):
            threshold = self.scoring.get_level_up_threshold(level)
            expected = level * game_config.speed["lines_per_level"]
            assert threshold == expected


class TestDASConfig:
    """Tests for Delayed Auto Shift configuration"""
    
    def test_das_delay(self):
        """Test DAS initial delay is 300ms"""
        assert game_config.das["delay_ms"] == 300
    
    def test_das_repeat(self):
        """Test DAS repeat rate is 100ms"""
        assert game_config.das["repeat_ms"] == 100
    
    def test_das_delay_in_seconds(self):
        """Test DAS delay converted to seconds"""
        delay_seconds = game_config.das["delay_ms"] / 1000
        assert delay_seconds == 0.3
    
    def test_das_repeat_in_seconds(self):
        """Test DAS repeat converted to seconds"""
        repeat_seconds = game_config.das["repeat_ms"] / 1000
        assert repeat_seconds == 0.1

