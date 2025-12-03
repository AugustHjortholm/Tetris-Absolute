"""
7-bag random piece generator.
This is the standard modern Tetris randomization algorithm.
Piece types loaded from config/game_config.json
"""

import random
from typing import List
from core.interfaces import IPieceGenerator, IPiece
from implementations.standard_piece import PieceFactory
from config import game_config


class SevenBagGenerator(IPieceGenerator):
    """
    7-bag random generator (standard modern Tetris).
    Generates a random permutation of all 7 pieces, then repeats.
    Ensures fair distribution and prevents long droughts.
    """
    
    def __init__(self):
        self._bag: List[str] = []
        self._next_piece: IPiece = None
        self._fill_bag()
        self._next_piece = self._generate_piece()
    
    def _fill_bag(self) -> None:
        """Fill the bag with all piece types from config"""
        self._bag = game_config.get_all_piece_types()[:]
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

