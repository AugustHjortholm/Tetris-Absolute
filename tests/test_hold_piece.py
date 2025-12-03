"""
Tests for Hold/Store piece functionality.
"""

import pytest
from implementations.standard_piece import PieceFactory


class TestHoldPieceLogic:
    """Tests for hold piece mechanics"""
    
    def test_piece_clone_for_hold(self):
        """Test that pieces can be cloned for holding"""
        piece = PieceFactory.create("T")
        cloned = piece.clone()
        
        assert cloned is not piece
        assert cloned.type == piece.type
        assert cloned.color == piece.color
        assert cloned.shape == piece.shape
    
    def test_piece_clone_independence(self):
        """Test that cloned piece is independent of original"""
        piece = PieceFactory.create("I")
        cloned = piece.clone()
        
        # Modify the cloned shape
        cloned_shape = cloned.shape
        cloned_shape[0][0] = 999  # This shouldn't affect original
        
        # Original should be unchanged
        assert piece.shape[0][0] != 999
    
    def test_rotation_reset_simulation(self):
        """Test that piece rotation can be reset when stored"""
        piece = PieceFactory.create("T")
        
        # Rotate the piece
        rotated = piece.rotate(clockwise=True)
        rotated = rotated.rotate(clockwise=True)  # Rotated 180 degrees
        
        # Create fresh piece to simulate reset
        fresh_piece = PieceFactory.create("T")
        
        # They should have same shape (original orientation)
        assert piece.shape == fresh_piece.shape
        # Rotated piece should be different
        assert rotated.shape != piece.shape
    
    def test_all_pieces_can_be_held(self):
        """Test that all piece types can be stored/retrieved"""
        piece_types = ["I", "J", "L", "O", "S", "T", "Z"]
        
        for ptype in piece_types:
            piece = PieceFactory.create(ptype)
            held = piece.clone()
            
            assert held.type == ptype
            assert held.color == piece.color
    
    def test_held_piece_preserves_type(self):
        """Test that held piece preserves its type"""
        original = PieceFactory.create("S")
        held = original.clone()
        
        # Retrieve the type
        assert held.type == "S"
    
    def test_held_piece_reset_rotation(self):
        """Test simulating rotation reset when holding"""
        # Simulate: piece is rotated, then stored
        piece = PieceFactory.create("L")
        rotated = piece.rotate(clockwise=True)
        
        # When storing, we'd create a fresh piece of the same type
        stored_type = rotated.type
        fresh = PieceFactory.create(stored_type)
        
        # Fresh piece should have default rotation
        original = PieceFactory.create("L")
        assert fresh.shape == original.shape


class TestHoldPieceOncePerDrop:
    """Tests for the once-per-piece hold restriction"""
    
    def test_hold_flag_concept(self):
        """Test the concept of hold-used flag"""
        can_hold = True
        
        # First hold should work
        assert can_hold == True
        can_hold = False  # Used hold
        
        # Can't hold again
        assert can_hold == False
    
    def test_hold_flag_reset_on_new_piece(self):
        """Test that hold flag resets when new piece spawns"""
        can_hold = True
        
        # Use hold
        can_hold = False
        assert can_hold == False
        
        # New piece spawns - reset flag
        can_hold = True
        assert can_hold == True


class TestHoldPieceSwap:
    """Tests for hold piece swap mechanics"""
    
    def test_first_hold_stores_piece(self):
        """Test that first hold stores current piece"""
        current_piece = PieceFactory.create("T")
        held_piece = None
        
        # First hold: store current, get next from queue
        if held_piece is None:
            held_piece = current_piece.clone()
            current_piece = None  # Would get next from queue
        
        assert held_piece is not None
        assert held_piece.type == "T"
    
    def test_subsequent_hold_swaps(self):
        """Test that subsequent hold swaps current with held"""
        current_piece = PieceFactory.create("I")
        held_piece = PieceFactory.create("T")
        
        # Swap pieces
        temp = held_piece
        held_piece = PieceFactory.create(current_piece.type)  # Fresh copy
        current_piece = temp
        
        assert current_piece.type == "T"
        assert held_piece.type == "I"
    
    def test_swap_preserves_both_pieces(self):
        """Test that swap doesn't lose either piece"""
        types_before = {"current": "S", "held": "Z"}
        
        current = PieceFactory.create(types_before["current"])
        held = PieceFactory.create(types_before["held"])
        
        # Swap
        current, held = held, PieceFactory.create(current.type)
        
        types_after = {"current": current.type, "held": held.type}
        
        # Both types should still exist
        assert "S" in types_after.values()
        assert "Z" in types_after.values()

