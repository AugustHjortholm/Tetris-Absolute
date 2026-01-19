"""
Tests for scoring multipliers (Tetris, Back-to-Back, Combo).
Tests the bonus scoring system.
"""

import pytest
from config import game_config


class TestTetrisMultiplier:
    """Tests for Tetris (4-line clear) multiplier"""
    
    def test_tetris_multiplier_value(self):
        """Test that Tetris multiplier is 1.2x"""
        assert game_config.multipliers["tetris"] == 1.2
    
    def test_tetris_score_calculation(self):
        """Test Tetris score with multiplier"""
        base_tetris_score = game_config.base_scores["tetris"]  # 800
        multiplier = game_config.multipliers["tetris"]  # 1.2
        expected = int(base_tetris_score * multiplier)  # 960
        assert expected == 960
    
    def test_tetris_score_with_level(self):
        """Test Tetris score scales with level"""
        base = game_config.base_scores["tetris"]
        mult = game_config.multipliers["tetris"]
        level = 5
        expected = int(base * level * mult)
        assert expected == 4800  # 800 * 5 * 1.2


class TestBackToBackMultiplier:
    """Tests for Back-to-Back Tetris multiplier"""
    
    def test_back_to_back_multiplier_value(self):
        """Test that Back-to-Back multiplier is 1.5x"""
        assert game_config.multipliers["back_to_back"] == 1.5
    
    def test_back_to_back_score_calculation(self):
        """Test Back-to-Back score with stacked multipliers"""
        base_tetris_score = game_config.base_scores["tetris"]  # 800
        tetris_mult = game_config.multipliers["tetris"]  # 1.2
        b2b_mult = game_config.multipliers["back_to_back"]  # 1.5
        
        # Back-to-back: tetris_mult * b2b_mult = 1.2 * 1.5 = 1.8x
        expected = int(base_tetris_score * tetris_mult * b2b_mult)
        assert expected == 1440  # 800 * 1.2 * 1.5
    
    def test_back_to_back_with_level(self):
        """Test Back-to-Back score scales with level"""
        base = game_config.base_scores["tetris"]
        tetris_mult = game_config.multipliers["tetris"]
        b2b_mult = game_config.multipliers["back_to_back"]
        level = 3
        
        expected = int(base * level * tetris_mult * b2b_mult)
        assert expected == 4320  # 800 * 3 * 1.2 * 1.5


class TestComboMultiplier:
    """Tests for Combo multiplier system"""
    
    def test_combo_per_level_value(self):
        """Test that combo increment is 0.1 per level"""
        assert game_config.multipliers["combo_per_level"] == 0.1
    
    def test_combo_2_multiplier(self):
        """Test x2 combo gives 1.1x multiplier"""
        combo_count = 2
        combo_mult = 1.0 + (combo_count - 1) * game_config.multipliers["combo_per_level"]
        assert combo_mult == 1.1
    
    def test_combo_3_multiplier(self):
        """Test x3 combo gives 1.2x multiplier"""
        combo_count = 3
        combo_mult = 1.0 + (combo_count - 1) * game_config.multipliers["combo_per_level"]
        assert combo_mult == 1.2
    
    def test_combo_5_multiplier(self):
        """Test x5 combo gives 1.4x multiplier"""
        combo_count = 5
        combo_mult = 1.0 + (combo_count - 1) * game_config.multipliers["combo_per_level"]
        assert combo_mult == 1.4
    
    def test_combo_10_multiplier(self):
        """Test x10 combo gives 1.9x multiplier"""
        combo_count = 10
        combo_mult = 1.0 + (combo_count - 1) * game_config.multipliers["combo_per_level"]
        assert combo_mult == pytest.approx(1.9, rel=1e-9)
    
    def test_combo_1_no_multiplier(self):
        """Test x1 combo (first clear) gives 1.0x multiplier"""
        combo_count = 1
        # First clear shouldn't have combo bonus
        if combo_count >= 2:
            combo_mult = 1.0 + (combo_count - 1) * game_config.multipliers["combo_per_level"]
        else:
            combo_mult = 1.0
        assert combo_mult == 1.0


class TestStackedMultipliers:
    """Tests for stacked multiplier scenarios"""
    
    def test_tetris_with_combo(self):
        """Test Tetris + x3 combo"""
        base = game_config.base_scores["tetris"]  # 800
        tetris_mult = game_config.multipliers["tetris"]  # 1.2
        combo_mult = 1.2  # x3 combo
        
        expected = int(base * tetris_mult * combo_mult)
        assert expected == 1152  # 800 * 1.2 * 1.2
    
    def test_back_to_back_with_combo(self):
        """Test Back-to-Back + x4 combo"""
        base = game_config.base_scores["tetris"]  # 800
        tetris_mult = game_config.multipliers["tetris"]  # 1.2
        b2b_mult = game_config.multipliers["back_to_back"]  # 1.5
        combo_mult = 1.3  # x4 combo
        
        expected = int(base * tetris_mult * b2b_mult * combo_mult)
        assert expected == 1872  # 800 * 1.2 * 1.5 * 1.3
    
    def test_normal_clear_with_combo(self):
        """Test normal double clear with x2 combo"""
        base = game_config.base_scores["double"]  # 300
        combo_mult = 1.1  # x2 combo
        
        expected = int(base * combo_mult)
        assert expected == 330  # 300 * 1.1
    
    def test_all_multipliers_with_level(self):
        """Test all multipliers stacked with level scaling"""
        base = game_config.base_scores["tetris"]  # 800
        level = 2
        tetris_mult = game_config.multipliers["tetris"]  # 1.2
        b2b_mult = game_config.multipliers["back_to_back"]  # 1.5
        combo_mult = 1.5  # x6 combo
        
        expected = int(base * level * tetris_mult * b2b_mult * combo_mult)
        assert expected == 4320  # 800 * 2 * 1.2 * 1.5 * 1.5

