"""
Unit tests for Piece implementations.
Tests piece creation, rotation, and properties.
"""

import pytest
from implementations.standard_piece import StandardPiece, PieceFactory


class TestStandardPiece:
    """Test the StandardPiece implementation"""
    
    def test_piece_creation(self):
        """Test creating a piece with basic properties"""
        shape = [[1, 1], [1, 1]]
        color = (255, 255, 0)
        piece = StandardPiece('O', color, shape)
        
        assert piece.type == 'O'
        assert piece.color == color
        assert piece.shape == shape
        assert piece.width == 2
        assert piece.height == 2
    
    def test_piece_rotation_clockwise(self):
        """Test rotating a piece clockwise"""
        # L piece
        shape = [
            [0, 0, 1],
            [1, 1, 1],
            [0, 0, 0],
        ]
        piece = StandardPiece('L', (255, 165, 0), shape)
        rotated = piece.rotate(clockwise=True)
        
        expected = [
            [0, 1, 0],
            [0, 1, 0],
            [0, 1, 1],
        ]
        
        assert rotated.shape == expected
        assert rotated.type == 'L'
        assert rotated.color == piece.color
    
    def test_piece_rotation_counter_clockwise(self):
        """Test rotating a piece counter-clockwise"""
        # L piece
        shape = [
            [0, 0, 1],
            [1, 1, 1],
            [0, 0, 0],
        ]
        piece = StandardPiece('L', (255, 165, 0), shape)
        rotated = piece.rotate(clockwise=False)
        
        expected = [
            [1, 1, 0],
            [0, 1, 0],
            [0, 1, 0],
        ]
        
        assert rotated.shape == expected
    
    def test_piece_rotation_full_circle(self):
        """Test rotating a piece 4 times returns to original"""
        shape = [
            [0, 0, 1],
            [1, 1, 1],
            [0, 0, 0],
        ]
        piece = StandardPiece('L', (255, 165, 0), shape)
        
        rotated = piece
        for _ in range(4):
            rotated = rotated.rotate(clockwise=True)
        
        assert rotated.shape == shape
    
    def test_piece_clone(self):
        """Test cloning a piece"""
        shape = [[1, 1], [1, 1]]
        piece = StandardPiece('O', (255, 255, 0), shape)
        cloned = piece.clone()
        
        assert cloned.type == piece.type
        assert cloned.color == piece.color
        assert cloned.shape == piece.shape
        assert cloned.shape is not piece.shape  # Different object


class TestPieceFactory:
    """Test the PieceFactory"""
    
    def test_create_all_pieces(self):
        """Test creating all 7 standard Tetris pieces"""
        piece_types = ['I', 'J', 'L', 'O', 'S', 'T', 'Z']
        
        for piece_type in piece_types:
            piece = PieceFactory.create(piece_type)
            assert piece.type == piece_type
            assert piece.color is not None
            assert len(piece.shape) > 0
    
    def test_create_i_piece(self):
        """Test creating I piece"""
        piece = PieceFactory.create('I')
        assert piece.type == 'I'
        assert piece.color == (0, 255, 255)  # Cyan
        assert piece.height == 4
        assert piece.width == 4
    
    def test_create_o_piece(self):
        """Test creating O piece"""
        piece = PieceFactory.create('O')
        assert piece.type == 'O'
        assert piece.color == (255, 255, 0)  # Yellow
        assert piece.height == 2
        assert piece.width == 2
    
    def test_create_t_piece(self):
        """Test creating T piece"""
        piece = PieceFactory.create('T')
        assert piece.type == 'T'
        assert piece.color == (128, 0, 128)  # Purple
        assert piece.height == 3
        assert piece.width == 3
    
    def test_get_all_types(self):
        """Test getting all piece types"""
        types = PieceFactory.get_all_types()
        assert len(types) == 7
        assert set(types) == {'I', 'J', 'L', 'O', 'S', 'T', 'Z'}
    
    def test_invalid_piece_type(self):
        """Test creating invalid piece type raises error"""
        with pytest.raises(ValueError):
            PieceFactory.create('X')

