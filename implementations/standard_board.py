"""
Standard Tetris board implementation.
"""

from typing import List, Tuple, Optional
from core.interfaces import IBoard, IPiece


class StandardBoard(IBoard):
    """Standard 10x20 Tetris board"""
    
    def __init__(self, width: int = 10, height: int = 20):
        self._width = width
        self._height = height
        self._grid: List[List[Optional[Tuple[int, int, int]]]] = self._create_empty_grid()
    
    def _create_empty_grid(self) -> List[List[Optional[Tuple[int, int, int]]]]:
        """Create an empty grid"""
        return [[None for _ in range(self._width)] for _ in range(self._height)]
    
    @property
    def width(self) -> int:
        return self._width
    
    @property
    def height(self) -> int:
        return self._height
    
    def get_cell(self, x: int, y: int) -> Optional[Tuple[int, int, int]]:
        """Get the color at a cell, or None if empty or out of bounds"""
        if x < 0 or x >= self._width or y < 0 or y >= self._height:
            return None
        return self._grid[y][x]
    
    def set_cell(self, x: int, y: int, color: Optional[Tuple[int, int, int]]) -> None:
        """Set the color at a cell"""
        if 0 <= x < self._width and 0 <= y < self._height:
            self._grid[y][x] = color
    
    def can_place_piece(self, piece: IPiece, x: int, y: int) -> bool:
        """Check if a piece can be placed at the given position"""
        shape = piece.shape
        
        for row in range(len(shape)):
            for col in range(len(shape[row])):
                if shape[row][col]:
                    board_x = x + col
                    board_y = y + row
                    
                    # Check horizontal bounds
                    if board_x < 0 or board_x >= self._width:
                        return False
                    
                    # Check bottom bound
                    if board_y >= self._height:
                        return False
                    
                    # Allow pieces above the board (for spawning)
                    if board_y < 0:
                        continue
                    
                    # Check collision with existing pieces
                    if self._grid[board_y][board_x] is not None:
                        return False
        
        return True
    
    def place_piece(self, piece: IPiece, x: int, y: int) -> None:
        """Place a piece on the board"""
        shape = piece.shape
        
        for row in range(len(shape)):
            for col in range(len(shape[row])):
                if shape[row][col]:
                    board_x = x + col
                    board_y = y + row
                    
                    if (0 <= board_y < self._height and 
                        0 <= board_x < self._width):
                        self._grid[board_y][board_x] = piece.color
    
    def get_full_rows(self) -> List[int]:
        """Get indices of all full rows"""
        full_rows = []
        
        for row in range(self._height):
            if all(cell is not None for cell in self._grid[row]):
                full_rows.append(row)
        
        return full_rows
    
    def clear_rows(self, rows: List[int]) -> None:
        """Clear the specified rows and move rows above down"""
        if not rows:
            return
        
        # Sort rows in descending order to avoid index shifting issues
        sorted_rows = sorted(rows, reverse=True)
        
        # Remove all the full rows
        for row in sorted_rows:
            del self._grid[row]
        
        # Add the same number of empty rows at the top
        for _ in range(len(rows)):
            self._grid.insert(0, [None for _ in range(self._width)])
    
    def clear(self) -> None:
        """Clear the entire board"""
        self._grid = self._create_empty_grid()
    
    def clone(self) -> 'StandardBoard':
        """Create a copy of the board"""
        cloned = StandardBoard(self._width, self._height)
        cloned._grid = [row[:] for row in self._grid]
        return cloned

