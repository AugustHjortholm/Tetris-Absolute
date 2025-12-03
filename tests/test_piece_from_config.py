"""
Tests for piece creation from JSON config.
"""

import pytest
from config import game_config
from implementations.standard_piece import PieceFactory


class TestPieceShapesFromConfig:
    """Tests for piece shapes loaded from config"""
    
    def test_i_piece_shape(self):
        """Test I piece shape from config"""
        shape = game_config.get_piece_shape("I")
        # I piece should be 4x4 with middle row filled
        assert len(shape) == 4
        assert len(shape[0]) == 4
        # Row 1 should be all 1s
        assert shape[1] == [1, 1, 1, 1]
    
    def test_o_piece_shape(self):
        """Test O piece shape from config"""
        shape = game_config.get_piece_shape("O")
        # O piece should be 2x2 all filled
        assert len(shape) == 2
        assert shape == [[1, 1], [1, 1]]
    
    def test_t_piece_shape(self):
        """Test T piece shape from config"""
        shape = game_config.get_piece_shape("T")
        # T piece should be 3x3
        assert len(shape) == 3
        assert shape[0] == [0, 1, 0]  # Top has center
        assert shape[1] == [1, 1, 1]  # Middle row full
    
    def test_s_piece_shape(self):
        """Test S piece shape from config"""
        shape = game_config.get_piece_shape("S")
        assert shape[0] == [0, 1, 1]
        assert shape[1] == [1, 1, 0]
    
    def test_z_piece_shape(self):
        """Test Z piece shape from config"""
        shape = game_config.get_piece_shape("Z")
        assert shape[0] == [1, 1, 0]
        assert shape[1] == [0, 1, 1]
    
    def test_j_piece_shape(self):
        """Test J piece shape from config"""
        shape = game_config.get_piece_shape("J")
        assert shape[0] == [1, 0, 0]  # Top left corner
        assert shape[1] == [1, 1, 1]  # Full row
    
    def test_l_piece_shape(self):
        """Test L piece shape from config"""
        shape = game_config.get_piece_shape("L")
        assert shape[0] == [0, 0, 1]  # Top right corner
        assert shape[1] == [1, 1, 1]  # Full row


class TestPieceColorsFromConfig:
    """Tests for piece colors loaded from config"""
    
    def test_i_piece_color(self):
        """Test I piece is cyan"""
        color = game_config.get_piece_color("I")
        assert color == (0, 255, 255)
    
    def test_j_piece_color(self):
        """Test J piece is blue"""
        color = game_config.get_piece_color("J")
        assert color == (0, 0, 255)
    
    def test_l_piece_color(self):
        """Test L piece is orange"""
        color = game_config.get_piece_color("L")
        assert color == (255, 165, 0)
    
    def test_o_piece_color(self):
        """Test O piece is yellow"""
        color = game_config.get_piece_color("O")
        assert color == (255, 255, 0)
    
    def test_s_piece_color(self):
        """Test S piece is green"""
        color = game_config.get_piece_color("S")
        assert color == (0, 255, 0)
    
    def test_t_piece_color(self):
        """Test T piece is purple"""
        color = game_config.get_piece_color("T")
        assert color == (128, 0, 128)
    
    def test_z_piece_color(self):
        """Test Z piece is red"""
        color = game_config.get_piece_color("Z")
        assert color == (255, 0, 0)


class TestPieceFactoryWithConfig:
    """Tests for PieceFactory using config"""
    
    def test_factory_creates_from_config(self):
        """Test that factory creates pieces with config values"""
        piece = PieceFactory.create("T")
        config_shape = game_config.get_piece_shape("T")
        config_color = game_config.get_piece_color("T")
        
        assert piece.shape == config_shape
        assert piece.color == config_color
    
    def test_factory_all_types_from_config(self):
        """Test that factory types match config"""
        factory_types = PieceFactory.get_all_types()
        config_types = game_config.get_all_piece_types()
        
        assert set(factory_types) == set(config_types)
    
    def test_all_pieces_match_config(self):
        """Test all pieces have correct config values"""
        for piece_type in game_config.get_all_piece_types():
            piece = PieceFactory.create(piece_type)
            
            assert piece.type == piece_type
            assert piece.color == game_config.get_piece_color(piece_type)
            assert piece.shape == game_config.get_piece_shape(piece_type)


class TestUIColorsFromConfig:
    """Tests for UI colors from config"""
    
    def test_background_color(self):
        """Test background color is loaded"""
        color = game_config.get_ui_color("background")
        assert isinstance(color, tuple)
        assert len(color) == 3
    
    def test_grid_color(self):
        """Test grid color is loaded"""
        color = game_config.get_ui_color("grid")
        assert isinstance(color, tuple)
    
    def test_text_colors(self):
        """Test text colors are loaded"""
        colors_to_test = [
            "text_primary",
            "text_gold",
            "text_tetris",
            "text_back_to_back",
            "text_combo"
        ]
        
        for color_name in colors_to_test:
            color = game_config.get_ui_color(color_name)
            assert isinstance(color, tuple)
            assert len(color) == 3
            # All RGB values should be 0-255
            for component in color:
                assert 0 <= component <= 255

