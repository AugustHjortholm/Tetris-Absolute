"""
Main game controller.
Orchestrates all game components with loose coupling.
"""

import time
from typing import Optional
from core.interfaces import (
    IBoard, IPiece, IPieceGenerator, IGameState,
    IRenderer, IInputHandler, IScoringSystem
)


class Game:
    """Main game controller"""
    
    def __init__(self,
                 board: IBoard,
                 piece_generator: IPieceGenerator,
                 game_state: IGameState,
                 renderer: IRenderer,
                 input_handler: IInputHandler,
                 scoring_system: IScoringSystem):
        
        self.board = board
        self.piece_generator = piece_generator
        self.game_state = game_state
        self.renderer = renderer
        self.input_handler = input_handler
        self.scoring_system = scoring_system
        
        self.current_piece: Optional[IPiece] = None
        self.current_x = 0
        self.current_y = 0
        
        self.held_piece: Optional[IPiece] = None
        self.can_hold = True  # Can only hold once per piece placement
        
        self.last_drop_time = 0.0
        self.drop_interval = 1.0
        
        self.running = False
    
    def start(self) -> None:
        """Start a new game"""
        self.game_state.reset()
        self.board.clear()
        self.piece_generator.reset()
        self.held_piece = None
        self.can_hold = True
        self._spawn_piece()
        self.last_drop_time = time.time()
        self._update_drop_interval()
        self.running = True
    
    def restart(self) -> None:
        """Restart the game"""
        self.start()
    
    def update(self) -> None:
        """Update game state"""
        # Check if game over
        if self.game_state.is_game_over:
            return
        
        # Check if paused
        if self.game_state.is_paused:
            return
        
        # Auto drop based on time
        current_time = time.time()
        if current_time - self.last_drop_time >= self.drop_interval:
            self._drop_piece()
            self.last_drop_time = current_time
    
    def handle_input(self) -> bool:
        """Handle input. Returns False if should quit."""
        if not self.input_handler.poll_events():
            return False
        
        # Handle restart
        if self.input_handler.should_restart():
            self.restart()
            return True
        
        # Handle pause
        if self.input_handler.should_pause():
            self._toggle_pause()
            return True
        
        # Don't handle game inputs if paused or game over
        if self.game_state.is_paused or self.game_state.is_game_over:
            return True
        
        # Handle movement
        if self.input_handler.should_move_left():
            self._move_left()
        
        if self.input_handler.should_move_right():
            self._move_right()
        
        if self.input_handler.should_move_down():
            self._move_down()
        
        if self.input_handler.should_rotate():
            self._rotate(clockwise=True)
        
        if hasattr(self.input_handler, 'should_rotate_left') and self.input_handler.should_rotate_left():
            self._rotate(clockwise=False)
        
        if self.input_handler.should_hard_drop():
            self._hard_drop()
        
        # Handle hold/store piece
        if hasattr(self.input_handler, 'should_hold') and self.input_handler.should_hold():
            self._hold_piece()
        
        return True
    
    def render(self) -> None:
        """Render the game"""
        self.renderer.clear()
        self.renderer.render_board(self.board)
        
        if self.current_piece:
            # Render ghost piece
            ghost_y = self._calculate_ghost_y()
            self.renderer.render_piece(self.current_piece, self.current_x, ghost_y, ghost=True)
            
            # Render current piece
            self.renderer.render_piece(self.current_piece, self.current_x, self.current_y)
        
        # Render next piece
        next_piece = self.piece_generator.peek()
        self.renderer.render_next_piece(next_piece)
        
        # Render held piece
        if hasattr(self.renderer, 'render_held_piece'):
            self.renderer.render_held_piece(self.held_piece)
        
        # Render game state
        self.renderer.render_game_state(self.game_state)
        
        # Render game over if needed
        if self.game_state.is_game_over:
            self.renderer.render_game_over()
        
        self.renderer.flip()
    
    def _spawn_piece(self) -> None:
        """Spawn a new piece"""
        self.current_piece = self.piece_generator.next()
        self.current_x = self.board.width // 2 - self.current_piece.width // 2
        self.current_y = 0
        
        # Check if piece can be placed (game over if not)
        if not self.board.can_place_piece(self.current_piece, self.current_x, self.current_y):
            self.game_state.set_game_over(True)
    
    def _drop_piece(self) -> None:
        """Drop the piece one row"""
        if not self.current_piece:
            return
        
        if self.board.can_place_piece(self.current_piece, self.current_x, self.current_y + 1):
            self.current_y += 1
        else:
            self._lock_piece()
    
    def _lock_piece(self) -> None:
        """Lock the current piece to the board"""
        if not self.current_piece:
            return
        
        self.board.place_piece(self.current_piece, self.current_x, self.current_y)
        
        # Re-enable hold after locking a piece
        self.can_hold = True
        
        # Check for line clears
        full_rows = self.board.get_full_rows()
        if full_rows:
            self.board.clear_rows(full_rows)
            score = self.scoring_system.calculate_score(len(full_rows), self.game_state.level)
            self.game_state.add_score(score)
            self.game_state.add_lines(len(full_rows))
            
            # Check for level up
            level_up_threshold = self.scoring_system.get_level_up_threshold(self.game_state.level)
            if self.game_state.lines >= level_up_threshold:
                self.game_state.increment_level()
                self._update_drop_interval()
        
        # Spawn next piece
        self._spawn_piece()
    
    def _move_left(self) -> None:
        """Move piece left"""
        if not self.current_piece:
            return
        
        if self.board.can_place_piece(self.current_piece, self.current_x - 1, self.current_y):
            self.current_x -= 1
    
    def _move_right(self) -> None:
        """Move piece right"""
        if not self.current_piece:
            return
        
        if self.board.can_place_piece(self.current_piece, self.current_x + 1, self.current_y):
            self.current_x += 1
    
    def _move_down(self) -> None:
        """Move piece down (soft drop)"""
        if not self.current_piece:
            return
        
        if self.board.can_place_piece(self.current_piece, self.current_x, self.current_y + 1):
            self.current_y += 1
            self.game_state.add_score(1)  # Soft drop points
    
    def _rotate(self, clockwise: bool = True) -> None:
        """Rotate the piece"""
        if not self.current_piece:
            return
        
        rotated = self.current_piece.rotate(clockwise=clockwise)
        
        # Try basic rotation
        if self.board.can_place_piece(rotated, self.current_x, self.current_y):
            self.current_piece = rotated
            return
        
        # Try wall kicks (simple version)
        kicks = [
            (-1, 0),   # Left
            (1, 0),    # Right
            (-2, 0),   # Left 2
            (2, 0),    # Right 2
            (0, -1),   # Up
        ]
        
        for kick_x, kick_y in kicks:
            if self.board.can_place_piece(rotated, self.current_x + kick_x, self.current_y + kick_y):
                self.current_piece = rotated
                self.current_x += kick_x
                self.current_y += kick_y
                return
    
    def _hard_drop(self) -> None:
        """Hard drop the piece"""
        if not self.current_piece:
            return
        
        drop_distance = 0
        while self.board.can_place_piece(self.current_piece, self.current_x, self.current_y + 1):
            self.current_y += 1
            drop_distance += 1
        
        self.game_state.add_score(drop_distance * 2)  # Hard drop points
        self._lock_piece()
    
    def _toggle_pause(self) -> None:
        """Toggle pause state"""
        if self.game_state.is_game_over:
            return
        
        if self.game_state.is_paused:
            self.game_state.resume()
            self.last_drop_time = time.time()  # Reset drop timer
        else:
            self.game_state.pause()
    
    def _update_drop_interval(self) -> None:
        """Update the drop interval based on level"""
        self.drop_interval = self.scoring_system.get_drop_speed(self.game_state.level)
    
    def _calculate_ghost_y(self) -> int:
        """Calculate the Y position for the ghost piece"""
        if not self.current_piece:
            return self.current_y
        
        ghost_y = self.current_y
        while self.board.can_place_piece(self.current_piece, self.current_x, ghost_y + 1):
            ghost_y += 1
        
        return ghost_y
    
    def _hold_piece(self) -> None:
        """Hold/store the current piece"""
        if not self.current_piece or not self.can_hold:
            return
        
        # Get the piece type to recreate it in default rotation
        from implementations.standard_piece import PieceFactory
        current_type = self.current_piece.type
        
        if self.held_piece is None:
            # First time holding - store current piece type and get next from queue
            self.held_piece = PieceFactory.create(current_type)
            self._spawn_piece()
        else:
            # Swap: get held piece type and recreate both in default rotation
            held_type = self.held_piece.type
            self.held_piece = PieceFactory.create(current_type)
            self.current_piece = PieceFactory.create(held_type)
            
            # Reset position for swapped piece
            self.current_x = self.board.width // 2 - self.current_piece.width // 2
            self.current_y = 0
            
            # Check if swapped piece can be placed (game over if not)
            if not self.board.can_place_piece(self.current_piece, self.current_x, self.current_y):
                self.game_state.set_game_over(True)
        
        # Can only hold once until piece is locked
        self.can_hold = False

