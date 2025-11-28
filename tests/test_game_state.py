"""
Unit tests for Game State implementation.
Tests score, level, and game state management.
"""

import pytest
from implementations.standard_game_state import StandardGameState


class TestStandardGameState:
    """Test the StandardGameState implementation"""
    
    def test_initialization(self):
        """Test game state initializes with correct defaults"""
        state = StandardGameState()
        
        assert state.score == 0
        assert state.level == 1
        assert state.lines == 0
        assert state.is_game_over == False
        assert state.is_paused == False
    
    def test_add_score(self):
        """Test adding to score"""
        state = StandardGameState()
        
        state.add_score(100)
        assert state.score == 100
        
        state.add_score(50)
        assert state.score == 150
    
    def test_add_lines(self):
        """Test adding cleared lines"""
        state = StandardGameState()
        
        state.add_lines(1)
        assert state.lines == 1
        
        state.add_lines(4)
        assert state.lines == 5
    
    def test_increment_level(self):
        """Test incrementing level"""
        state = StandardGameState()
        
        assert state.level == 1
        state.increment_level()
        assert state.level == 2
        state.increment_level()
        assert state.level == 3
    
    def test_pause_resume(self):
        """Test pausing and resuming"""
        state = StandardGameState()
        
        assert state.is_paused == False
        
        state.pause()
        assert state.is_paused == True
        
        state.resume()
        assert state.is_paused == False
    
    def test_set_game_over(self):
        """Test setting game over state"""
        state = StandardGameState()
        
        assert state.is_game_over == False
        
        state.set_game_over(True)
        assert state.is_game_over == True
        
        state.set_game_over(False)
        assert state.is_game_over == False
    
    def test_reset(self):
        """Test resetting game state"""
        state = StandardGameState()
        
        # Modify state
        state.add_score(1000)
        state.add_lines(10)
        state.increment_level()
        state.increment_level()
        state.set_game_over(True)
        state.pause()
        
        # Reset
        state.reset()
        
        # Should be back to defaults
        assert state.score == 0
        assert state.level == 1
        assert state.lines == 0
        assert state.is_game_over == False
        assert state.is_paused == False

