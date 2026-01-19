"""
Tests for the configuration loading system.
Tests game_config.json and localization loading.
"""

import pytest
from config import game_config, localization, hex_to_rgb, GameConfig, Localization


class TestHexToRgb:
    """Tests for hex color conversion"""
    
    def test_hex_to_rgb_with_hash(self):
        """Test conversion with # prefix"""
        assert hex_to_rgb("#FF0000") == (255, 0, 0)
        assert hex_to_rgb("#00FF00") == (0, 255, 0)
        assert hex_to_rgb("#0000FF") == (0, 0, 255)
    
    def test_hex_to_rgb_without_hash(self):
        """Test conversion without # prefix"""
        assert hex_to_rgb("FF0000") == (255, 0, 0)
        assert hex_to_rgb("FFFFFF") == (255, 255, 255)
        assert hex_to_rgb("000000") == (0, 0, 0)
    
    def test_hex_to_rgb_mixed_case(self):
        """Test with mixed case hex"""
        assert hex_to_rgb("#FfAa00") == (255, 170, 0)
        assert hex_to_rgb("aAbBcC") == (170, 187, 204)


class TestGameConfig:
    """Tests for GameConfig singleton"""
    
    def test_singleton_pattern(self):
        """Test that GameConfig is a singleton"""
        config1 = GameConfig()
        config2 = GameConfig()
        assert config1 is config2
    
    def test_base_scores_exist(self):
        """Test that base scores are loaded"""
        scores = game_config.base_scores
        assert "single" in scores
        assert "double" in scores
        assert "triple" in scores
        assert "tetris" in scores
    
    def test_base_scores_values(self):
        """Test base score values are reasonable"""
        scores = game_config.base_scores
        assert scores["single"] == 100
        assert scores["double"] == 300
        assert scores["triple"] == 500
        assert scores["tetris"] == 800
    
    def test_multipliers_exist(self):
        """Test that multipliers are loaded"""
        mults = game_config.multipliers
        assert "tetris" in mults
        assert "back_to_back" in mults
        assert "combo_per_level" in mults
    
    def test_multipliers_values(self):
        """Test multiplier values"""
        mults = game_config.multipliers
        assert mults["tetris"] == 1.2
        assert mults["back_to_back"] == 1.5
        assert mults["combo_per_level"] == 0.1
    
    def test_speed_config_exists(self):
        """Test that speed config is loaded"""
        speed = game_config.speed
        assert "base_drop_interval" in speed
        assert "min_drop_interval" in speed
        assert "speed_decrease_per_level" in speed
        assert "soft_drop_multiplier" in speed
        assert "lines_per_level" in speed
    
    def test_lock_delay_config_exists(self):
        """Test that lock delay config is loaded"""
        lock = game_config.lock_delay
        assert "base_delay" in lock
        assert "max_delay" in lock
        assert "soft_drop_multiplier" in lock
    
    def test_das_config_exists(self):
        """Test that DAS config is loaded"""
        das = game_config.das
        assert "delay_ms" in das
        assert "repeat_ms" in das
        assert das["delay_ms"] == 300
        assert das["repeat_ms"] == 100
    
    def test_board_config_exists(self):
        """Test that board config is loaded"""
        board = game_config.board
        assert "width" in board
        assert "height" in board
        assert "cell_size" in board
        assert board["width"] == 10
        assert board["height"] == 20
    
    def test_get_piece_color(self):
        """Test getting piece colors"""
        i_color = game_config.get_piece_color("I")
        assert i_color == (0, 255, 255)  # Cyan
        
        t_color = game_config.get_piece_color("T")
        assert t_color == (128, 0, 128)  # Purple
    
    def test_get_ui_color(self):
        """Test getting UI colors"""
        bg = game_config.get_ui_color("background")
        assert isinstance(bg, tuple)
        assert len(bg) == 3
    
    def test_get_piece_shape(self):
        """Test getting piece shapes"""
        i_shape = game_config.get_piece_shape("I")
        assert len(i_shape) == 4  # I piece is 4x4
        assert len(i_shape[0]) == 4
        
        o_shape = game_config.get_piece_shape("O")
        assert len(o_shape) == 2  # O piece is 2x2
        assert len(o_shape[0]) == 2
    
    def test_get_all_piece_types(self):
        """Test getting all piece types"""
        types = game_config.get_all_piece_types()
        assert "I" in types
        assert "J" in types
        assert "L" in types
        assert "O" in types
        assert "S" in types
        assert "T" in types
        assert "Z" in types
        assert len(types) == 7
    
    def test_notification_duration(self):
        """Test notification duration is loaded"""
        duration = game_config.notification_duration
        assert duration == 1.5


class TestLocalization:
    """Tests for Localization singleton"""
    
    def test_singleton_pattern(self):
        """Test that Localization is a singleton"""
        loc1 = Localization()
        loc2 = Localization()
        assert loc1 is loc2
    
    def test_get_ui_labels(self):
        """Test getting UI labels"""
        assert localization.get("ui", "score") == "SCORE"
        assert localization.get("ui", "level") == "LEVEL"
        assert localization.get("ui", "lines") == "LINES"
        assert localization.get("ui", "next") == "NEXT"
        assert localization.get("ui", "hold") == "HOLD"
    
    def test_get_game_states(self):
        """Test getting game state text"""
        assert localization.get("game_states", "paused") == "PAUSED"
        assert localization.get("game_states", "game_over") == "GAME OVER"
        assert "restart" in localization.get("game_states", "press_restart").lower()
    
    def test_get_notifications(self):
        """Test getting notification text"""
        assert localization.get("notifications", "tetris") == "TETRIS!"
        assert localization.get("notifications", "back_to_back") == "BACK-TO-BACK!"
    
    def test_get_with_placeholder(self):
        """Test getting text with placeholder substitution"""
        combo_text = localization.get("notifications", "combo", count=5)
        assert "5" in combo_text
        assert "COMBO" in combo_text
    
    def test_get_missing_key_returns_placeholder(self):
        """Test that missing keys return a placeholder"""
        result = localization.get("nonexistent", "key")
        assert "[" in result and "]" in result
    
    def test_current_language(self):
        """Test that current language is set"""
        assert localization.current_language == "en"

