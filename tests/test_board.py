"""
Unit tests for the Board implementation.
Tests board operations, piece placement, and line clearing.
"""

import pytest
from implementations.standard_board import StandardBoard
from implementations.standard_piece import PieceFactory


class TestStandardBoard:
    """Test the StandardBoard implementation"""
    
    def test_board_initialization(self):
        """Test board is created with correct dimensions"""
        board = StandardBoard(10, 20)
        assert board.width == 10
        assert board.height == 20
        
        # Check all cells are empty
        for y in range(board.height):
            for x in range(board.width):
                assert board.get_cell(x, y) is None
    
    def test_custom_dimensions(self):
        """Test board with custom dimensions"""
        board = StandardBoard(8, 15)
        assert board.width == 8
        assert board.height == 15
    
    def test_set_and_get_cell(self):
        """Test setting and getting cell values"""
        board = StandardBoard(10, 20)
        color = (255, 0, 0)  # Red
        
        board.set_cell(5, 10, color)
        assert board.get_cell(5, 10) == color
        
        # Test out of bounds returns None
        assert board.get_cell(-1, 0) is None
        assert board.get_cell(0, -1) is None
        assert board.get_cell(10, 0) is None
        assert board.get_cell(0, 20) is None
    
    def test_can_place_piece(self):
        """Test piece placement validation"""
        board = StandardBoard(10, 20)
        piece = PieceFactory.create('I')
        
        # Should be able to place at top center
        assert board.can_place_piece(piece, 3, 0)
        
        # Should not be able to place out of bounds
        assert not board.can_place_piece(piece, -1, 0)
        assert not board.can_place_piece(piece, 10, 0)
        assert not board.can_place_piece(piece, 0, 20)
    
    def test_can_place_piece_with_collision(self):
        """Test piece placement with existing pieces"""
        board = StandardBoard(10, 20)
        piece = PieceFactory.create('O')
        
        # Place a piece
        board.place_piece(piece, 0, 18)
        
        # Should not be able to place another piece in the same location
        assert not board.can_place_piece(piece, 0, 18)
        
        # Should be able to place next to it
        assert board.can_place_piece(piece, 2, 18)
    
    def test_place_piece(self):
        """Test placing a piece on the board"""
        board = StandardBoard(10, 20)
        piece = PieceFactory.create('O')  # 2x2 square
        
        board.place_piece(piece, 0, 18)
        
        # Check that cells are filled
        assert board.get_cell(0, 18) == piece.color
        assert board.get_cell(1, 18) == piece.color
        assert board.get_cell(0, 19) == piece.color
        assert board.get_cell(1, 19) == piece.color
        
        # Check adjacent cells are empty
        assert board.get_cell(2, 18) is None
    
    def test_get_full_rows_none(self):
        """Test getting full rows when there are none"""
        board = StandardBoard(10, 20)
        assert board.get_full_rows() == []
    
    def test_get_full_rows_single(self):
        """Test detecting a single full row"""
        board = StandardBoard(10, 20)
        
        # Fill bottom row
        color = (255, 0, 0)
        for x in range(10):
            board.set_cell(x, 19, color)
        
        full_rows = board.get_full_rows()
        assert full_rows == [19]
    
    def test_get_full_rows_multiple(self):
        """Test detecting multiple full rows"""
        board = StandardBoard(10, 20)
        
        # Fill bottom two rows
        color = (255, 0, 0)
        for x in range(10):
            board.set_cell(x, 18, color)
            board.set_cell(x, 19, color)
        
        full_rows = board.get_full_rows()
        assert full_rows == [18, 19]
    
    def test_get_full_rows_non_consecutive(self):
        """Test detecting non-consecutive full rows"""
        board = StandardBoard(10, 20)
        
        # Fill rows 17 and 19 but not 18
        color = (255, 0, 0)
        for x in range(10):
            board.set_cell(x, 17, color)
            board.set_cell(x, 19, color)
        
        full_rows = board.get_full_rows()
        assert sorted(full_rows) == [17, 19]
    
    def test_clear_single_row(self):
        """Test clearing a single row"""
        board = StandardBoard(10, 20)
        
        # Fill bottom row and place piece above it
        bottom_color = (255, 0, 0)
        for x in range(10):
            board.set_cell(x, 19, bottom_color)
        
        above_color = (0, 255, 0)
        board.set_cell(5, 18, above_color)
        
        # Clear bottom row
        board.clear_rows([19])
        
        # Check piece above moved down to row 19
        assert board.get_cell(5, 19) == above_color
        assert board.get_cell(5, 18) is None
        
        # Check rest of bottom row is empty
        for x in range(10):
            if x != 5:
                assert board.get_cell(x, 19) is None
    
    def test_clear_multiple_rows(self):
        """Test clearing multiple rows at once"""
        board = StandardBoard(10, 20)
        
        # Fill bottom three rows
        color1 = (255, 0, 0)
        color2 = (0, 255, 0)
        color3 = (0, 0, 255)
        
        for x in range(10):
            board.set_cell(x, 17, color1)
            board.set_cell(x, 18, color2)
            board.set_cell(x, 19, color3)
        
        # Place a piece above
        above_color = (255, 255, 0)
        board.set_cell(5, 16, above_color)
        
        # Clear all three rows
        board.clear_rows([17, 18, 19])
        
        # Check piece moved down 3 rows
        assert board.get_cell(5, 19) == above_color
        assert board.get_cell(5, 16) is None
        
        # Check rest of rows 17-19 are empty
        for row in [17, 18, 19]:
            for x in range(10):
                if not (row == 19 and x == 5):
                    assert board.get_cell(x, row) is None
    
    def test_clear_non_consecutive_rows(self):
        """Test clearing non-consecutive rows (the bug we fixed)"""
        board = StandardBoard(10, 20)
        
        # Fill rows 17 and 19
        color1 = (255, 0, 0)
        color2 = (0, 0, 255)
        
        for x in range(10):
            board.set_cell(x, 17, color1)
            board.set_cell(x, 19, color2)
        
        # Put something in row 18 (not full)
        partial_color = (0, 255, 0)
        board.set_cell(5, 18, partial_color)
        
        # Clear rows 17 and 19
        board.clear_rows([17, 19])
        
        # Partial piece from row 18 should have moved down 2 rows to row 19
        # (row 19 was cleared, then row 18 moved down 1, then row 17 was cleared,
        #  so row 18 moved down again)
        assert board.get_cell(5, 19) == partial_color
        assert board.get_cell(5, 18) is None
        
        # Rest of row 19 should be empty
        for x in range(10):
            if x != 5:
                assert board.get_cell(x, 19) is None
        
        # Rows 17 and 18 should be completely empty
        for x in range(10):
            assert board.get_cell(x, 17) is None
            assert board.get_cell(x, 18) is None
    
    def test_clear_four_rows_tetris(self):
        """Test clearing 4 rows at once (Tetris)"""
        board = StandardBoard(10, 20)
        
        # Fill bottom 4 rows
        for row in range(16, 20):
            for x in range(10):
                board.set_cell(x, row, (255, 0, 0))
        
        # Place marker above
        board.set_cell(5, 15, (0, 255, 0))
        
        # Clear all 4 rows
        board.clear_rows([16, 17, 18, 19])
        
        # Marker should have moved down 4 rows
        assert board.get_cell(5, 19) == (0, 255, 0)
        assert board.get_cell(5, 15) is None
        
        # Rest of bottom 4 rows should be empty
        for row in range(16, 20):
            for x in range(10):
                if not (row == 19 and x == 5):
                    assert board.get_cell(x, row) is None
    
    def test_clear_board(self):
        """Test clearing the entire board"""
        board = StandardBoard(10, 20)
        
        # Fill some cells
        for x in range(5):
            for y in range(10):
                board.set_cell(x, y, (255, 0, 0))
        
        # Clear board
        board.clear()
        
        # Check all cells are empty
        for y in range(board.height):
            for x in range(board.width):
                assert board.get_cell(x, y) is None
    
    def test_clone_board(self):
        """Test cloning a board"""
        board = StandardBoard(10, 20)
        
        # Fill some cells
        board.set_cell(5, 10, (255, 0, 0))
        board.set_cell(3, 15, (0, 255, 0))
        
        # Clone
        cloned = board.clone()
        
        # Check dimensions match
        assert cloned.width == board.width
        assert cloned.height == board.height
        
        # Check cells match
        assert cloned.get_cell(5, 10) == (255, 0, 0)
        assert cloned.get_cell(3, 15) == (0, 255, 0)
        
        # Modify clone and ensure original unchanged
        cloned.set_cell(5, 10, (0, 0, 255))
        assert board.get_cell(5, 10) == (255, 0, 0)
        assert cloned.get_cell(5, 10) == (0, 0, 255)

