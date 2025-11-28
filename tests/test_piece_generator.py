"""
Unit tests for Piece Generator implementations.
Tests the 7-bag randomizer.
"""

import pytest
from implementations.seven_bag_generator import SevenBagGenerator
from implementations.standard_piece import PieceFactory


class TestSevenBagGenerator:
    """Test the SevenBagGenerator (modern Tetris randomization)"""
    
    def test_generator_initialization(self):
        """Test generator initializes and has a next piece"""
        generator = SevenBagGenerator()
        next_piece = generator.peek()
        
        assert next_piece is not None
        assert next_piece.type in PieceFactory.get_all_types()
    
    def test_next_returns_piece(self):
        """Test next() returns valid pieces"""
        generator = SevenBagGenerator()
        
        for _ in range(10):
            piece = generator.next()
            assert piece is not None
            assert piece.type in PieceFactory.get_all_types()
    
    def test_peek_doesnt_consume(self):
        """Test peek() doesn't consume the next piece"""
        generator = SevenBagGenerator()
        
        peeked1 = generator.peek()
        peeked2 = generator.peek()
        
        # Peek should return the same piece type
        assert peeked1.type == peeked2.type
        
        # Next should return that same piece
        actual = generator.next()
        assert actual.type == peeked1.type
    
    def test_seven_bag_contains_all_pieces(self):
        """Test that every 7 pieces contains all 7 types"""
        generator = SevenBagGenerator()
        
        # Get 7 pieces
        pieces = [generator.next() for _ in range(7)]
        types = [p.type for p in pieces]
        
        # Should have all 7 types
        assert set(types) == set(PieceFactory.get_all_types())
    
    def test_multiple_bags_all_pieces(self):
        """Test multiple bags all contain all pieces"""
        generator = SevenBagGenerator()
        
        for bag in range(3):
            pieces = [generator.next() for _ in range(7)]
            types = [p.type for p in pieces]
            assert set(types) == set(PieceFactory.get_all_types()), \
                f"Bag {bag} didn't contain all pieces"
    
    def test_reset(self):
        """Test reset() resets the generator"""
        generator = SevenBagGenerator()
        
        # Generate some pieces
        for _ in range(5):
            generator.next()
        
        # Reset
        generator.reset()
        
        # Should still be able to generate pieces
        piece = generator.next()
        assert piece is not None
        assert piece.type in PieceFactory.get_all_types()
    
    def test_randomization(self):
        """Test that pieces are randomized (not always same order)"""
        # This test has a very small chance of false failure
        # but it's astronomically unlikely
        
        # Generate two sequences of 7 pieces
        gen1 = SevenBagGenerator()
        gen2 = SevenBagGenerator()
        
        seq1 = [gen1.next().type for _ in range(7)]
        seq2 = [gen2.next().type for _ in range(7)]
        
        # They should (almost certainly) be different orders
        # If they're the same, try again
        if seq1 == seq2:
            gen3 = SevenBagGenerator()
            seq3 = [gen3.next().type for _ in range(7)]
            assert seq1 != seq3, "Sequences not randomized"

