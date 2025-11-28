"""
Core interfaces for the Tetris Roguelike game.
Using Abstract Base Classes (ABC) to enforce contracts between components.
This ensures low coupling and easy extensibility for roguelike features.
"""

from abc import ABC, abstractmethod
from typing import List, Tuple


class IPiece(ABC):
    """
    Interface for a Tetris piece (tetromino).
    Allows for different piece behaviors (e.g., special pieces in roguelike mode).
    """
    
    @property
    @abstractmethod
    def type(self) -> str:
        """The type identifier of the piece (I, J, L, O, S, T, Z, etc.)"""
        pass
    
    @property
    @abstractmethod
    def color(self) -> Tuple[int, int, int]:
        """RGB color tuple"""
        pass
    
    @property
    @abstractmethod
    def shape(self) -> List[List[int]]:
        """2D array representing the piece shape"""
        pass
    
    @property
    @abstractmethod
    def width(self) -> int:
        """Width of the piece"""
        pass
    
    @property
    @abstractmethod
    def height(self) -> int:
        """Height of the piece"""
        pass
    
    @abstractmethod
    def rotate(self, clockwise: bool = True) -> 'IPiece':
        """Rotate the piece and return a new piece instance"""
        pass
    
    @abstractmethod
    def clone(self) -> 'IPiece':
        """Create a copy of the piece"""
        pass


class IBoard(ABC):
    """
    Interface for the game board.
    Different implementations can have different board sizes or behaviors.
    """
    
    @property
    @abstractmethod
    def width(self) -> int:
        """Board width in cells"""
        pass
    
    @property
    @abstractmethod
    def height(self) -> int:
        """Board height in cells"""
        pass
    
    @abstractmethod
    def get_cell(self, x: int, y: int) -> Tuple[int, int, int] | None:
        """Get the color at a cell position, or None if empty"""
        pass
    
    @abstractmethod
    def set_cell(self, x: int, y: int, color: Tuple[int, int, int] | None) -> None:
        """Set the color at a cell position"""
        pass
    
    @abstractmethod
    def can_place_piece(self, piece: IPiece, x: int, y: int) -> bool:
        """Check if a piece can be placed at the given position"""
        pass
    
    @abstractmethod
    def place_piece(self, piece: IPiece, x: int, y: int) -> None:
        """Place a piece on the board"""
        pass
    
    @abstractmethod
    def get_full_rows(self) -> List[int]:
        """Get a list of row indices that are completely filled"""
        pass
    
    @abstractmethod
    def clear_rows(self, rows: List[int]) -> None:
        """Clear the specified rows"""
        pass
    
    @abstractmethod
    def clear(self) -> None:
        """Clear the entire board"""
        pass
    
    @abstractmethod
    def clone(self) -> 'IBoard':
        """Create a copy of the board"""
        pass


class IPieceGenerator(ABC):
    """
    Interface for generating pieces.
    Different implementations can use different algorithms (7-bag, pure random, weighted, etc.)
    Essential for roguelike modifiers that affect piece distribution.
    """
    
    @abstractmethod
    def next(self) -> IPiece:
        """Get the next piece"""
        pass
    
    @abstractmethod
    def peek(self) -> IPiece:
        """Peek at the next piece without consuming it"""
        pass
    
    @abstractmethod
    def reset(self) -> None:
        """Reset the generator"""
        pass


class IGameState(ABC):
    """
    Interface for game state management.
    Allows different game modes to have different state implementations.
    """
    
    @property
    @abstractmethod
    def score(self) -> int:
        pass
    
    @property
    @abstractmethod
    def level(self) -> int:
        pass
    
    @property
    @abstractmethod
    def lines(self) -> int:
        pass
    
    @property
    @abstractmethod
    def is_game_over(self) -> bool:
        pass
    
    @property
    @abstractmethod
    def is_paused(self) -> bool:
        pass
    
    @abstractmethod
    def add_score(self, points: int) -> None:
        """Add points to the score"""
        pass
    
    @abstractmethod
    def add_lines(self, count: int) -> None:
        """Add cleared lines"""
        pass
    
    @abstractmethod
    def increment_level(self) -> None:
        """Increase the level"""
        pass
    
    @abstractmethod
    def pause(self) -> None:
        """Pause the game"""
        pass
    
    @abstractmethod
    def resume(self) -> None:
        """Resume the game"""
        pass
    
    @abstractmethod
    def set_game_over(self, game_over: bool) -> None:
        """Set game over state"""
        pass
    
    @abstractmethod
    def reset(self) -> None:
        """Reset the game state"""
        pass


class IRenderer(ABC):
    """
    Interface for rendering the game.
    Allows swapping rendering implementations.
    """
    
    @abstractmethod
    def render_board(self, board: IBoard) -> None:
        """Render the game board"""
        pass
    
    @abstractmethod
    def render_piece(self, piece: IPiece, x: int, y: int, ghost: bool = False) -> None:
        """Render a piece at the given position"""
        pass
    
    @abstractmethod
    def render_next_piece(self, piece: IPiece) -> None:
        """Render the next piece preview"""
        pass
    
    @abstractmethod
    def render_game_state(self, state: IGameState) -> None:
        """Render score, level, lines, etc."""
        pass
    
    @abstractmethod
    def render_game_over(self) -> None:
        """Render game over screen"""
        pass
    
    @abstractmethod
    def clear(self) -> None:
        """Clear the screen"""
        pass
    
    @abstractmethod
    def flip(self) -> None:
        """Update the display"""
        pass


class IInputHandler(ABC):
    """
    Interface for handling input.
    Allows different input methods (keyboard, gamepad, touch, AI, etc.)
    """
    
    @abstractmethod
    def poll_events(self) -> bool:
        """Poll for events. Returns False if quit event detected."""
        pass
    
    @abstractmethod
    def should_move_left(self) -> bool:
        pass
    
    @abstractmethod
    def should_move_right(self) -> bool:
        pass
    
    @abstractmethod
    def should_move_down(self) -> bool:
        pass
    
    @abstractmethod
    def should_rotate(self) -> bool:
        pass
    
    @abstractmethod
    def should_hard_drop(self) -> bool:
        pass
    
    @abstractmethod
    def should_pause(self) -> bool:
        pass
    
    @abstractmethod
    def should_restart(self) -> bool:
        pass


class IScoringSystem(ABC):
    """
    Interface for scoring systems.
    Different implementations can have different scoring rules.
    Essential for roguelike modifiers that affect scoring.
    """
    
    @abstractmethod
    def calculate_score(self, lines_cleared: int, level: int, 
                       soft_drop: int = 0, hard_drop: int = 0) -> int:
        """Calculate score based on lines cleared and drop distance"""
        pass
    
    @abstractmethod
    def get_level_up_threshold(self, current_level: int) -> int:
        """Get the number of lines needed to level up"""
        pass
    
    @abstractmethod
    def get_drop_speed(self, level: int) -> float:
        """Get the drop speed in seconds for a given level"""
        pass

