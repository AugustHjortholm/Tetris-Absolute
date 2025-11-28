"""
Standard Tetris piece implementations.
Includes the 7 standard tetrominoes.
"""

from typing import List, Tuple
from core.interfaces import IPiece


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
    """Factory for creating standard Tetris pieces"""
    
    # Standard Tetris pieces with their shapes and colors
    PIECES = {
        'I': {
            'color': (0, 255, 255),  # Cyan
            'shape': [
                [0, 0, 0, 0],
                [1, 1, 1, 1],
                [0, 0, 0, 0],
                [0, 0, 0, 0],
            ]
        },
        'J': {
            'color': (0, 0, 255),  # Blue
            'shape': [
                [1, 0, 0],
                [1, 1, 1],
                [0, 0, 0],
            ]
        },
        'L': {
            'color': (255, 165, 0),  # Orange
            'shape': [
                [0, 0, 1],
                [1, 1, 1],
                [0, 0, 0],
            ]
        },
        'O': {
            'color': (255, 255, 0),  # Yellow
            'shape': [
                [1, 1],
                [1, 1],
            ]
        },
        'S': {
            'color': (0, 255, 0),  # Green
            'shape': [
                [0, 1, 1],
                [1, 1, 0],
                [0, 0, 0],
            ]
        },
        'T': {
            'color': (128, 0, 128),  # Purple
            'shape': [
                [0, 1, 0],
                [1, 1, 1],
                [0, 0, 0],
            ]
        },
        'Z': {
            'color': (255, 0, 0),  # Red
            'shape': [
                [1, 1, 0],
                [0, 1, 1],
                [0, 0, 0],
            ]
        },
    }
    
    @staticmethod
    def create(piece_type: str) -> StandardPiece:
        """Create a piece by type"""
        if piece_type not in PieceFactory.PIECES:
            raise ValueError(f"Unknown piece type: {piece_type}")
        
        piece_data = PieceFactory.PIECES[piece_type]
        return StandardPiece(piece_type, piece_data['color'], piece_data['shape'])
    
    @staticmethod
    def get_all_types() -> List[str]:
        """Get all available piece types"""
        return list(PieceFactory.PIECES.keys())

