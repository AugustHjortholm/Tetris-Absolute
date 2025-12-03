"""
Main game controller.
Orchestrates all game components with loose coupling.
Settings loaded from config/game_config.json
"""

import time
from typing import Optional
from core.interfaces import (
    IBoard, IPiece, IPieceGenerator, IGameState,
    IRenderer, IInputHandler, IScoringSystem
)
from config import game_config


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
        self.drop_interval = game_config.speed["base_drop_interval"]
        self.soft_drop_multiplier = game_config.speed["soft_drop_multiplier"]
        self.is_soft_dropping = False
        
        # Lock delay system from config
        lock_delay_config = game_config.lock_delay
        self.lock_delay = lock_delay_config["base_delay"]
        self.max_lock_delay = lock_delay_config["max_delay"]
        self.lock_delay_timer = 0.0
        self.total_lock_delay_timer = 0.0
        self.is_grounded = False
        self.lock_delay_start_time = 0.0
        self.total_lock_delay_start_time = 0.0
        self.soft_drop_lock_multiplier = lock_delay_config["soft_drop_multiplier"]
        
        # Scoring multipliers from config
        self.tetris_multiplier = game_config.multipliers["tetris"]
        self.back_to_back_multiplier = game_config.multipliers["back_to_back"]
        self.combo_multiplier_per_level = game_config.multipliers["combo_per_level"]
        self.last_clear_was_tetris = False
        self.combo_count = 0
        
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
        self.return_to_menu = False
    
    def restart(self) -> None:
        """Restart the game"""
        self.start()
    
    def request_menu(self) -> None:
        """Request to return to the main menu"""
        self.return_to_menu = True
        self.running = False
    
    def update(self) -> None:
        """Update game state"""
        # Check if game over
        if self.game_state.is_game_over:
            return
        
        # Check if paused
        if self.game_state.is_paused:
            return
        
        current_time = time.time()
        
        # Check if piece is grounded (touching bottom or another piece)
        if self.current_piece:
            grounded = not self.board.can_place_piece(
                self.current_piece, 
                self.current_x, 
                self.current_y + 1
            )
            
            if grounded and not self.is_grounded:
                # Just became grounded - start lock delay
                self.is_grounded = True
                self.lock_delay_start_time = current_time
                if self.total_lock_delay_start_time == 0.0:
                    self.total_lock_delay_start_time = current_time
            elif not grounded:
                # Piece is no longer grounded
                self.is_grounded = False
                self.lock_delay_start_time = 0.0
            
            # Handle lock delay
            if self.is_grounded:
                time_since_grounded = current_time - self.lock_delay_start_time
                total_time_grounded = current_time - self.total_lock_delay_start_time
                
                # Reduce lock delay when soft dropping
                current_lock_delay = self.lock_delay
                current_max_lock_delay = self.max_lock_delay
                if self.is_soft_dropping:
                    current_lock_delay = self.lock_delay / self.soft_drop_lock_multiplier
                    current_max_lock_delay = self.max_lock_delay / self.soft_drop_lock_multiplier
                
                # Lock if either timer expires
                if time_since_grounded >= current_lock_delay or total_time_grounded >= current_max_lock_delay:
                    self._lock_piece()
                    return
        
        # Update soft drop state from input handler
        if self.current_piece:
            self.is_soft_dropping = self.input_handler.should_move_down()
        
        # Auto drop based on time (with soft drop speed multiplier)
        current_drop_interval = self.drop_interval
        if self.is_soft_dropping:
            current_drop_interval = self.drop_interval / self.soft_drop_multiplier
        
        if current_time - self.last_drop_time >= current_drop_interval:
            self._drop_piece()
            self.last_drop_time = current_time
            
            # Add soft drop points only when actually dropping
            if self.is_soft_dropping and self.current_piece:
                self.game_state.add_score(1)
    
    def handle_input(self) -> bool:
        """Handle input. Returns False if should quit."""
        if not self.input_handler.poll_events():
            return False
        
        # Handle return to menu (was restart)
        if self.input_handler.should_restart():
            self.request_menu()
            return False  # Stop the game loop
        
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
        
        # Soft drop is now handled in update() with speed multiplier
        # No need to call _move_down() here anymore
        
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
        
        # Render points notification if active
        if hasattr(self.renderer, 'render_points_notification'):
            self.renderer.render_points_notification()
        
        # Render combo notification if active
        if hasattr(self.renderer, 'render_combo_notification'):
            self.renderer.render_combo_notification()
        
        # Render pause overlay if paused
        if self.game_state.is_paused:
            if hasattr(self.renderer, 'render_paused'):
                self.renderer.render_paused()
        
        # Render game over if needed
        if self.game_state.is_game_over:
            self.renderer.render_game_over()
        
        self.renderer.flip()
    
    def _spawn_piece(self) -> None:
        """Spawn a new piece"""
        self.current_piece = self.piece_generator.next()
        self.current_x = self.board.width // 2 - self.current_piece.width // 2
        self.current_y = 0
        
        # Reset lock delay timers
        self.is_grounded = False
        self.lock_delay_start_time = 0.0
        self.total_lock_delay_start_time = 0.0
        
        # Reset soft drop state for new piece
        self.is_soft_dropping = False

        # Check if piece can be placed (game over if not)
        if not self.board.can_place_piece(self.current_piece, self.current_x, self.current_y):
            self.game_state.set_game_over(True)
    
    def _drop_piece(self) -> None:
        """Drop the piece one row"""
        if not self.current_piece:
            return
        
        if self.board.can_place_piece(self.current_piece, self.current_x, self.current_y + 1):
            self.current_y += 1
            # Reset lock delay if piece moves down
            if self.is_grounded:
                self.lock_delay_start_time = time.time()
    
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
            lines_cleared = len(full_rows)
            
            # Calculate base score
            base_score = self.scoring_system.calculate_score(lines_cleared, self.game_state.level)
            
            # Check for special clears
            is_tetris = lines_cleared == 4
            is_back_to_back = is_tetris and self.last_clear_was_tetris
            
            # Update combo first (so we can apply multiplier)
            self.combo_count += 1
            
            # Calculate combo multiplier from config
            # combo 1 = 1.0x, combo 2 = 1.0 + 0.1, combo 3 = 1.0 + 0.2, etc.
            combo_multiplier = 1.0
            if self.combo_count >= 2:
                combo_multiplier = 1.0 + (self.combo_count - 1) * self.combo_multiplier_per_level
            
            # Apply multipliers from config
            final_score = base_score
            special_type = None
            
            if is_back_to_back:
                # Back-to-back Tetris: tetris_mult * b2b_mult * combo_mult
                final_score = int(base_score * self.tetris_multiplier * self.back_to_back_multiplier * combo_multiplier)
                special_type = "back_to_back"
            elif is_tetris:
                # Tetris: tetris_mult * combo_mult
                final_score = int(base_score * self.tetris_multiplier * combo_multiplier)
                special_type = "tetris"
            else:
                # Normal clear with combo multiplier
                final_score = int(base_score * combo_multiplier)
            
            # Add score
            self.game_state.add_score(final_score)
            self.game_state.add_lines(lines_cleared)
            
            # Track Tetris for back-to-back detection
            self.last_clear_was_tetris = is_tetris
            
            # Show points notification with special type
            if hasattr(self.renderer, 'show_points_notification'):
                self.renderer.show_points_notification(final_score, special_type)
            
            # Show combo notification if combo >= 2
            if self.combo_count >= 2 and hasattr(self.renderer, 'show_combo_notification'):
                self.renderer.show_combo_notification(self.combo_count, combo_multiplier)
        else:
            # No lines cleared - reset combo
            self.combo_count = 0
            
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
            # Reset lock delay timer on movement
            if self.is_grounded:
                self.lock_delay_start_time = time.time()
    
    def _move_right(self) -> None:
        """Move piece right"""
        if not self.current_piece:
            return
        
        if self.board.can_place_piece(self.current_piece, self.current_x + 1, self.current_y):
            self.current_x += 1
            # Reset lock delay timer on movement
            if self.is_grounded:
                self.lock_delay_start_time = time.time()
    
    def _move_down(self) -> None:
        """Move piece down (no longer used for soft drop, kept for compatibility)"""
        # Soft drop is now handled by the drop speed multiplier in update()
        pass
    
    def _rotate(self, clockwise: bool = True) -> None:
        """Rotate the piece"""
        if not self.current_piece:
            return
        
        rotated = self.current_piece.rotate(clockwise=clockwise)
        
        # Try basic rotation
        if self.board.can_place_piece(rotated, self.current_x, self.current_y):
            self.current_piece = rotated
            # Reset lock delay timer on rotation
            if self.is_grounded:
                self.lock_delay_start_time = time.time()
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
                # Reset lock delay timer on rotation
                if self.is_grounded:
                    self.lock_delay_start_time = time.time()
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

