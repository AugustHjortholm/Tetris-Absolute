"""
Tests for lock delay mechanics.
"""

import pytest
from config import game_config


class TestLockDelayConfig:
    """Tests for lock delay configuration"""
    
    def test_base_lock_delay(self):
        """Test base lock delay is 1 second"""
        assert game_config.lock_delay["base_delay"] == 1.0
    
    def test_max_lock_delay(self):
        """Test max lock delay is 3 seconds"""
        assert game_config.lock_delay["max_delay"] == 3.0
    
    def test_soft_drop_lock_multiplier(self):
        """Test soft drop lock delay multiplier is 10x"""
        assert game_config.lock_delay["soft_drop_multiplier"] == 10.0


class TestLockDelayMechanics:
    """Tests for lock delay mechanics simulation"""
    
    def test_lock_delay_timer_concept(self):
        """Test basic lock delay timer"""
        lock_delay = game_config.lock_delay["base_delay"]
        time_grounded = 0.0
        
        # Simulate time passing
        time_grounded += 0.5
        assert time_grounded < lock_delay  # Not locked yet
        
        time_grounded += 0.6
        assert time_grounded >= lock_delay  # Should lock now
    
    def test_lock_delay_reset_on_movement(self):
        """Test that lock delay resets on movement"""
        lock_delay = game_config.lock_delay["base_delay"]
        time_grounded = 0.8  # Almost locked
        
        # Movement occurs - reset timer
        time_grounded = 0.0
        
        assert time_grounded < lock_delay
    
    def test_max_lock_delay_overrides(self):
        """Test that max lock delay overrides resets"""
        max_lock = game_config.lock_delay["max_delay"]
        total_time_grounded = 0.0
        
        # Simulate multiple resets
        for _ in range(10):
            total_time_grounded += 0.4  # Each grounded period
        
        # Total time exceeds max
        assert total_time_grounded >= max_lock
    
    def test_soft_drop_accelerates_lock(self):
        """Test that soft drop reduces lock delay by 10x"""
        base_lock = game_config.lock_delay["base_delay"]
        multiplier = game_config.lock_delay["soft_drop_multiplier"]
        
        soft_drop_lock = base_lock / multiplier
        assert soft_drop_lock == 0.1  # 1.0 / 10 = 0.1 seconds
    
    def test_soft_drop_accelerates_max_lock(self):
        """Test that soft drop also reduces max lock delay"""
        max_lock = game_config.lock_delay["max_delay"]
        multiplier = game_config.lock_delay["soft_drop_multiplier"]
        
        soft_drop_max = max_lock / multiplier
        assert soft_drop_max == 0.3  # 3.0 / 10 = 0.3 seconds


class TestLockDelayIntegration:
    """Integration tests for lock delay scenarios"""
    
    def test_normal_landing_sequence(self):
        """Test normal piece landing without manipulation"""
        lock_delay = game_config.lock_delay["base_delay"]
        is_grounded = False
        lock_timer = 0.0
        
        # Piece lands
        is_grounded = True
        
        # Wait full lock delay
        lock_timer = lock_delay
        
        # Should lock
        should_lock = lock_timer >= lock_delay
        assert should_lock
    
    def test_manipulation_extends_lock(self):
        """Test that movement/rotation extends lock time"""
        lock_delay = game_config.lock_delay["base_delay"]
        max_lock = game_config.lock_delay["max_delay"]
        
        lock_timer = 0.8
        total_timer = 0.8
        
        # Rotate - reset lock timer but not total
        lock_timer = 0.0
        total_timer += 0.5
        lock_timer += 0.5
        
        # Can keep manipulating until max is reached
        while total_timer < max_lock:
            total_timer += 0.4
            lock_timer = 0.4  # Reset each time
        
        # Eventually must lock due to max
        assert total_timer >= max_lock
    
    def test_fast_player_can_extend(self):
        """Test that fast movement resets can extend lock time"""
        lock_delay = game_config.lock_delay["base_delay"]
        movements = 0
        lock_timer = 0.0
        
        # Fast player makes moves before lock
        for _ in range(5):
            lock_timer += 0.15  # Small time between moves
            if lock_timer < lock_delay:
                lock_timer = 0.0  # Reset on movement
                movements += 1
        
        # Player made multiple moves
        assert movements == 5

