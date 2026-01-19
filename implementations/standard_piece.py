"""
Standard Tetris piece implementations.
Includes the 7 standard tetrominoes.
Piece definitions loaded from config/game_config.json
"""

from typing import List, Tuple
from core.interfaces import IPiece
from config import game_config


class StandardPiece(IPiece):
    """Standard Tetris piece implementation"""
    
    def __init__(self, piece_type: str, color: Tuple[int, int, int], shape: List[List[int]]):
        self._type = piece_type
        self._color = color
        self._shape = shape
    
    @property
    def type(self) -> str:
        return self._type
    
    @property
    def color(self) -> Tuple[int, int, int]:
        return self._color
    
    @property
    def shape(self) -> List[List[int]]:
        return self._shape
    
    @property
    def width(self) -> int:
        return len(self._shape[0])
    
    @property
    def height(self) -> int:
        return len(self._shape)
    
    def rotate(self, clockwise: bool = True) -> 'StandardPiece':
        """Rotate the piece 90 degrees"""
        new_shape = self._rotate_matrix(self._shape, clockwise)
        return StandardPiece(self._type, self._color, new_shape)
    
    def _rotate_matrix(self, matrix: List[List[int]], clockwise: bool) -> List[List[int]]:
        """Rotate a 2D matrix"""
        rows = len(matrix)
        cols = len(matrix[0])
        
        if clockwise:
            # Rotate 90 degrees clockwise: transpose and reverse each row
            rotated = [[matrix[rows - 1 - row][col] for row in range(rows)] 
                      for col in range(cols)]
        else:
            # Rotate 90 degrees counter-clockwise: reverse and transpose
            rotated = [[matrix[row][cols - 1 - col] for row in range(rows)] 
                      for col in range(cols)]
        
        return rotated
    
    def clone(self) -> 'StandardPiece':
        """Create a copy of the piece"""
        shape_copy = [row[:] for row in self._shape]
        return StandardPiece(self._type, self._color, shape_copy)


class PieceFactory:
    """Factory for creating Tetris pieces from config"""
    
    # Custom pieces added by cards
    _custom_pieces: dict = {}
    
    @classmethod
    def register_custom_piece(cls, piece_id: str, shape: List[List[int]], color: Tuple[int, int, int]) -> None:
        """Register a custom piece type from a card"""
        cls._custom_pieces[piece_id] = {
            "shape": shape,
            "color": color
        }
    
    @classmethod
    def clear_custom_pieces(cls) -> None:
        """Clear all custom pieces (on game restart)"""
        cls._custom_pieces.clear()
    
    @staticmethod
    def create(piece_type: str) -> StandardPiece:
        """Create a piece by type from config or custom pieces"""
        # Check custom pieces first
        if piece_type in PieceFactory._custom_pieces:
            custom = PieceFactory._custom_pieces[piece_type]
            return StandardPiece(piece_type, custom["color"], custom["shape"])
        
        # Check standard pieces
        all_types = game_config.get_all_piece_types()
        if piece_type not in all_types:
            raise ValueError(f"Unknown piece type: {piece_type}")
        
        color = game_config.get_piece_color(piece_type)
        shape = game_config.get_piece_shape(piece_type)
        return StandardPiece(piece_type, color, shape)
    
    @staticmethod
    def get_all_types() -> List[str]:
        """Get all available piece types from config and custom"""
        base_types = game_config.get_all_piece_types()
        custom_types = list(PieceFactory._custom_pieces.keys())
        return base_types + custom_types

