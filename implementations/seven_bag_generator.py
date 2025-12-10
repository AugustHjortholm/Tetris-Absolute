"""
7-bag random piece generator.
This is the standard modern Tetris randomization algorithm.
Piece types loaded from config/game_config.json
Supports extra pieces from roguelike cards.
"""

import random
from typing import List, Optional, Dict, Any
from core.interfaces import IPieceGenerator, IPiece
from implementations.standard_piece import PieceFactory
from config import game_config


class SevenBagGenerator(IPieceGenerator):
    """
    7-bag random generator (standard modern Tetris).
    Generates a random permutation of all 7 pieces, then repeats.
    Ensures fair distribution and prevents long droughts.
    Supports extra pieces from roguelike card system.
    """
    
    def __init__(self):
        self._bag: List[str] = []
        self._next_piece: IPiece = None
        self._extra_pieces: List[Dict[str, Any]] = []  # Cards can add pieces
        self._removed_types: List[str] = []  # Cards can remove pieces
        self._fill_bag()
        self._next_piece = self._generate_piece()
    
    def add_extra_piece(self, piece_id: str, shape: List[List[int]], color: str) -> None:
        """Add an extra piece type from a card"""
        self._extra_pieces.append({
            "id": piece_id,
            "shape": shape,
            "color": color
        })
    
    def inject_next_piece(self, piece_id: str) -> None:
        """Replace the next piece with a specific piece type (for blue cards)"""
        self._next_piece = PieceFactory.create(piece_id)
    
    def remove_piece_type(self, piece_type: str) -> None:
        """Remove a piece type from the bag"""
        if piece_type not in self._removed_types:
            self._removed_types.append(piece_type)
    
    def _get_available_types(self) -> List[str]:
        """Get all available piece types including extras, excluding removed"""
        base_types = [t for t in game_config.get_all_piece_types() 
                      if t not in self._removed_types]
        extra_types = [p["id"] for p in self._extra_pieces]
        return base_types + extra_types
    
    def _fill_bag(self) -> None:
        """Fill the bag with all piece types from config"""
        self._bag = self._get_available_types()[:]
        random.shuffle(self._bag)
    
    def _generate_piece(self) -> IPiece:
        """Generate the next piece from the bag"""
        if not self._bag:
            self._fill_bag()
        
        piece_type = self._bag.pop()
        return PieceFactory.create(piece_type)
    
    def next(self) -> IPiece:
        """Get the next piece"""
        current = self._next_piece
        self._next_piece = self._generate_piece()
        return current
    
    def peek(self) -> IPiece:
        """Peek at the next piece without consuming it"""
        return self._next_piece.clone()
    
    def reset(self) -> None:
        """Reset the generator"""
        self._bag = []
        self._fill_bag()
        self._next_piece = self._generate_piece()

