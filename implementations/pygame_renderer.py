"""
Pygame-based renderer for the Tetris game.
Colors and text loaded from config files.
"""

import pygame
from typing import Tuple, Optional
from core.interfaces import IRenderer, IBoard, IPiece, IGameState
from config import game_config, localization


class PygameRenderer(IRenderer):
    """Pygame implementation of the renderer using config values"""
    
    def __init__(self, screen: pygame.Surface, cell_size: int = None, use_controller: bool = False):
        self.screen = screen
        self.cell_size = cell_size or game_config.board["cell_size"]
        self.use_controller = use_controller
        
        # Calculate layout
        # Board is centered with panels on left and right
        self.hold_panel_x = 20  # Hold panel on far left
        self.board_x = self.hold_panel_x + 180 + 20  # Board after hold panel
        self.board_y = 20
        
        # Side panel position (right side)
        self.panel_x = self.board_x + game_config.board["width"] * self.cell_size + 40
        self.panel_y = 20
        
        self.hold_panel_y = 20
        
        # Font setup
        pygame.font.init()
        self.font_large = pygame.font.Font(None, 48)
        self.font_medium = pygame.font.Font(None, 36)
        self.font_small = pygame.font.Font(None, 24)
        
        # Colors from config
        self.bg_color = game_config.get_ui_color("background")
        self.grid_color = game_config.get_ui_color("grid")
        self.text_color = game_config.get_ui_color("text_primary")
        self.panel_bg = game_config.get_ui_color("panel_background")
        self.text_gold = game_config.get_ui_color("text_gold")
        self.text_tetris = game_config.get_ui_color("text_tetris")
        self.text_b2b = game_config.get_ui_color("text_back_to_back")
        self.text_combo = game_config.get_ui_color("text_combo")
        self.text_combo_mult = game_config.get_ui_color("text_combo_multiplier")
        
        # Points notification
        self.points_notification = None  # (points, start_time, special_type)
        self.points_notification_duration = game_config.notification_duration
        
        # Combo notification
        self.combo_notification = None  # (combo_count, start_time, multiplier)
        self.combo_notification_duration = game_config.notification_duration
    
    def clear(self) -> None:
        """Clear the screen"""
        self.screen.fill(self.bg_color)
    
    def render_board(self, board: IBoard) -> None:
        """Render the game board"""
        # Draw board background
        board_width = board.width * self.cell_size
        board_height = board.height * self.cell_size
        pygame.draw.rect(self.screen, (0, 0, 0), 
                        (self.board_x, self.board_y, board_width, board_height))
        
        # Draw cells
        for y in range(board.height):
            for x in range(board.width):
                color = board.get_cell(x, y)
                if color is not None:
                    self._draw_cell(x, y, color)
        
        # Draw grid lines
        self._draw_grid(board.width, board.height)
    
    def render_piece(self, piece: IPiece, x: int, y: int, ghost: bool = False) -> None:
        """Render a piece at the given position"""
        shape = piece.shape
        color = piece.color
        
        for row in range(len(shape)):
            for col in range(len(shape[row])):
                if shape[row][col]:
                    draw_x = x + col
                    draw_y = y + row
                    
                    if draw_y >= 0:  # Only draw if on screen
                        if ghost:
                            self._draw_ghost_cell(draw_x, draw_y, color)
                        else:
                            self._draw_cell(draw_x, draw_y, color)
    
    def render_next_piece(self, piece: IPiece) -> None:
        """Render the next piece preview"""
        # Draw panel background
        panel_rect = pygame.Rect(self.panel_x, self.panel_y + 300, 160, 160)
        pygame.draw.rect(self.screen, self.panel_bg, panel_rect)
        pygame.draw.rect(self.screen, self.grid_color, panel_rect, 2)
        
        # Draw "NEXT" label
        label = self.font_small.render(localization.get("ui", "next"), True, self.text_gold)
        self.screen.blit(label, (self.panel_x + 10, self.panel_y + 270))
        
        # Draw the piece centered in the panel
        self._draw_piece_preview(piece, self.panel_x, self.panel_y + 320, 160, 120)
    
    def render_held_piece(self, piece: Optional[IPiece], disabled: bool = False) -> None:
        """Render the held piece preview"""
        # Draw panel background
        panel_rect = pygame.Rect(self.hold_panel_x, self.hold_panel_y, 160, 160)
        pygame.draw.rect(self.screen, self.panel_bg, panel_rect)
        pygame.draw.rect(self.screen, self.grid_color, panel_rect, 2)
        
        # Draw "HOLD" label (red if disabled)
        label_color = (255, 100, 100) if disabled else self.text_gold
        label = self.font_small.render(localization.get("ui", "hold"), True, label_color)
        self.screen.blit(label, (self.hold_panel_x + 10, self.hold_panel_y + 10))
        
        # Draw the piece if one is held
        if piece is not None and not disabled:
            self._draw_piece_preview(piece, self.hold_panel_x, self.hold_panel_y + 40, 160, 120)
        elif disabled:
            # Draw X over the hold panel
            x1, y1 = self.hold_panel_x + 30, self.hold_panel_y + 50
            x2, y2 = self.hold_panel_x + 130, self.hold_panel_y + 140
            pygame.draw.line(self.screen, (255, 100, 100), (x1, y1), (x2, y2), 3)
            pygame.draw.line(self.screen, (255, 100, 100), (x2, y1), (x1, y2), 3)
    
    def render_speed_level(self, speed_level: int) -> None:
        """Render the current card speed level"""
        # Position above controls
        y = self.panel_y + 470
        
        # Draw speed level indicator
        label = self.font_small.render("SPEED", True, self.text_gold)
        self.screen.blit(label, (self.hold_panel_x + 10, y))
        
        # Speed value with color based on level
        if speed_level <= 3:
            color = (100, 255, 100)  # Green - easy
        elif speed_level <= 6:
            color = (255, 255, 100)  # Yellow - medium
        elif speed_level <= 9:
            color = (255, 165, 0)  # Orange - hard
        else:
            color = (255, 100, 100)  # Red - very hard
        
        value = self.font_medium.render(str(speed_level), True, color)
        self.screen.blit(value, (self.hold_panel_x + 10, y + 22))
    
    def render_collected_cards(self, collected_cards: list) -> None:
        """Render the list of collected cards as colored rectangles"""
        from config import cards_config
        
        if not collected_cards:
            return
        
        # Position below speed level on left side
        start_x = self.hold_panel_x
        start_y = self.hold_panel_y + 180  # Below hold panel
        
        # Card rectangle dimensions
        card_width = 25
        card_height = 35
        cards_per_row = 6
        spacing_x = 3
        spacing_y = 3
        
        # Draw "CARDS" label
        label = self.font_small.render("CARDS", True, self.text_gold)
        self.screen.blit(label, (start_x + 10, start_y))
        start_y += 25
        
        # Draw each collected card as a colored rectangle
        for i, card in enumerate(collected_cards):
            row = i // cards_per_row
            col = i % cards_per_row
            
            x = start_x + col * (card_width + spacing_x)
            y = start_y + row * (card_height + spacing_y)
            
            # Get border color for this card type
            card_type = card.type.value
            border_color = cards_config.get_card_color(card_type, "border")
            bg_color = cards_config.get_card_color(card_type, "background")
            
            # Draw background rectangle
            pygame.draw.rect(self.screen, bg_color, 
                           (x, y, card_width, card_height))
            
            # Draw border
            pygame.draw.rect(self.screen, border_color, 
                           (x, y, card_width, card_height), 2)
    
    def _draw_piece_preview(self, piece: IPiece, panel_x: int, panel_y: int, 
                           panel_width: int, panel_height: int) -> None:
        """Helper method to draw a piece preview in a panel"""
        shape = piece.shape
        small_cell_size = 25
        
        # Calculate centering offset
        piece_width = len(shape[0]) * small_cell_size
        piece_height = len(shape) * small_cell_size
        offset_x = panel_x + (panel_width - piece_width) // 2
        offset_y = panel_y + (panel_height - piece_height) // 2
        
        for row in range(len(shape)):
            for col in range(len(shape[row])):
                if shape[row][col]:
                    x = offset_x + col * small_cell_size
                    y = offset_y + row * small_cell_size
                    
                    # Draw cell
                    pygame.draw.rect(self.screen, piece.color, 
                                   (x, y, small_cell_size - 2, small_cell_size - 2))
                    # Draw border
                    pygame.draw.rect(self.screen, (255, 255, 255), 
                                   (x, y, small_cell_size - 2, small_cell_size - 2), 1)
    
    def render_game_state(self, state: IGameState) -> None:
        """Render score, level, lines, etc."""
        y_offset = self.panel_y
        
        # Score
        self._draw_stat_panel(localization.get("ui", "score"), str(state.score), y_offset)
        y_offset += 80
        
        # Level
        self._draw_stat_panel(localization.get("ui", "level"), str(state.level), y_offset)
        y_offset += 80
        
        # Lines
        self._draw_stat_panel(localization.get("ui", "lines"), str(state.lines), y_offset)
        
        # Controls (at bottom)
        self._draw_controls()
    
    def render_game_over(self) -> None:
        """Render game over screen"""
        # Semi-transparent overlay from config
        overlay = pygame.Surface(self.screen.get_size())
        overlay.set_alpha(game_config.get_game_over_color("overlay_alpha"))
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))
        
        # "GAME OVER" text from localization
        game_over_color = game_config.get_ui_color("text_primary")
        # Try to get game over specific color, fallback to red
        try:
            game_over_color = game_config.get_game_over_color("text")
            if isinstance(game_over_color, str):
                from config import hex_to_rgb
                game_over_color = hex_to_rgb(game_over_color)
        except:
            game_over_color = (255, 0, 0)
        
        game_over_text = self.font_large.render(
            localization.get("game_states", "game_over"), 
            True, 
            game_over_color
        )
        text_rect = game_over_text.get_rect(center=(self.screen.get_width() // 2, 
                                                     self.screen.get_height() // 2 - 30))
        self.screen.blit(game_over_text, text_rect)
        
        # "Press R for Menu" text from localization
        menu_text = self.font_small.render(
            localization.get("game_states", "press_menu"), 
            True, 
            self.text_color
        )
        menu_rect = menu_text.get_rect(center=(self.screen.get_width() // 2, 
                                                self.screen.get_height() // 2 + 30))
        self.screen.blit(menu_text, menu_rect)
    
    def show_points_notification(self, points: int, special_type: str = None) -> None:
        """Show a points notification for line clears"""
        import time
        self.points_notification = (points, time.time(), special_type)
    
    def show_combo_notification(self, combo_count: int, multiplier: float = 1.0) -> None:
        """Show a combo notification"""
        import time
        self.combo_notification = (combo_count, time.time(), multiplier)
    
    def render_points_notification(self) -> None:
        """Render the points notification if active"""
        if self.points_notification is None:
            return
        
        import time
        points, start_time, special_type = self.points_notification
        elapsed = time.time() - start_time
        
        if elapsed >= self.points_notification_duration:
            self.points_notification = None
            return
        
        # Calculate fade (starts fully visible, fades out)
        alpha = int(255 * (1 - elapsed / self.points_notification_duration))
        
        # Determine color and text based on special type
        if special_type == "back_to_back":
            color = self.text_b2b
            special_text = localization.get("notifications", "back_to_back")
        elif special_type == "tetris":
            color = self.text_tetris
            special_text = localization.get("notifications", "tetris")
        else:
            color = self.text_gold
            special_text = None
        
        # Render points text
        points_text = f"+{points}"
        text_surface = self.font_medium.render(points_text, True, color)
        
        # Create a surface with alpha for fading
        text_with_alpha = pygame.Surface(text_surface.get_size(), pygame.SRCALPHA)
        text_with_alpha.blit(text_surface, (0, 0))
        text_with_alpha.set_alpha(alpha)
        
        # Position below the score panel
        x = self.panel_x + 10
        y = self.panel_y + 75  # Below the score panel
        
        self.screen.blit(text_with_alpha, (x, y))
        
        # Render special text if applicable
        if special_text:
            special_surface = self.font_small.render(special_text, True, color)
            special_with_alpha = pygame.Surface(special_surface.get_size(), pygame.SRCALPHA)
            special_with_alpha.blit(special_surface, (0, 0))
            special_with_alpha.set_alpha(alpha)
            self.screen.blit(special_with_alpha, (x, y + 30))
    
    def render_combo_notification(self) -> None:
        """Render the combo notification if active"""
        if self.combo_notification is None:
            return
        
        import time
        combo_count, start_time, multiplier = self.combo_notification
        elapsed = time.time() - start_time
        
        if elapsed >= self.combo_notification_duration:
            self.combo_notification = None
            return
        
        # Calculate fade (starts fully visible, fades out)
        alpha = int(255 * (1 - elapsed / self.combo_notification_duration))
        
        # Render combo text with multiplier
        combo_text = localization.get("notifications", "combo", count=combo_count)
        multiplier_text = localization.get("notifications", "multiplier", value=f"{multiplier:.1f}")
        color = self.text_combo
        
        # Combo text
        text_surface = self.font_small.render(combo_text, True, color)
        text_with_alpha = pygame.Surface(text_surface.get_size(), pygame.SRCALPHA)
        text_with_alpha.blit(text_surface, (0, 0))
        text_with_alpha.set_alpha(alpha)
        
        # Multiplier text
        mult_surface = self.font_small.render(multiplier_text, True, self.text_combo_mult)
        mult_with_alpha = pygame.Surface(mult_surface.get_size(), pygame.SRCALPHA)
        mult_with_alpha.blit(mult_surface, (0, 0))
        mult_with_alpha.set_alpha(alpha)
        
        # Position below the lines panel (different from Tetris/Back-to-back)
        x = self.panel_x + 10
        y = self.panel_y + 255  # Below the lines panel
        
        self.screen.blit(text_with_alpha, (x, y))
        self.screen.blit(mult_with_alpha, (x, y + 18))
    
    def render_paused(self) -> None:
        """Render pause overlay with darkened screen"""
        # Semi-transparent dark overlay from config
        overlay = pygame.Surface(self.screen.get_size())
        overlay.set_alpha(game_config.get_pause_color("overlay_alpha"))
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))
        
        # "PAUSED" text from localization
        pause_color = game_config.get_ui_color("text_primary")
        paused_text = self.font_large.render(
            localization.get("game_states", "paused"), 
            True, 
            pause_color
        )
        text_rect = paused_text.get_rect(center=(self.screen.get_width() // 2, 
                                                  self.screen.get_height() // 2))
        self.screen.blit(paused_text, text_rect)
    
    def flip(self) -> None:
        """Update the display"""
        pygame.display.flip()
    
    def _draw_cell(self, x: int, y: int, color: Tuple[int, int, int]) -> None:
        """Draw a single cell"""
        pixel_x = self.board_x + x * self.cell_size
        pixel_y = self.board_y + y * self.cell_size
        
        # Draw filled rectangle
        pygame.draw.rect(self.screen, color, 
                        (pixel_x, pixel_y, self.cell_size - 1, self.cell_size - 1))
        
        # Draw border for depth effect
        pygame.draw.rect(self.screen, (255, 255, 255), 
                        (pixel_x, pixel_y, self.cell_size - 1, self.cell_size - 1), 1)
    
    def _draw_ghost_cell(self, x: int, y: int, color: Tuple[int, int, int]) -> None:
        """Draw a ghost (transparent) cell"""
        pixel_x = self.board_x + x * self.cell_size
        pixel_y = self.board_y + y * self.cell_size
        
        # Draw just the outline
        pygame.draw.rect(self.screen, color, 
                        (pixel_x, pixel_y, self.cell_size - 1, self.cell_size - 1), 2)
    
    def _draw_grid(self, width: int, height: int) -> None:
        """Draw grid lines"""
        # Vertical lines
        for x in range(width + 1):
            pixel_x = self.board_x + x * self.cell_size
            pygame.draw.line(self.screen, self.grid_color, 
                           (pixel_x, self.board_y), 
                           (pixel_x, self.board_y + height * self.cell_size))
        
        # Horizontal lines
        for y in range(height + 1):
            pixel_y = self.board_y + y * self.cell_size
            pygame.draw.line(self.screen, self.grid_color, 
                           (self.board_x, pixel_y), 
                           (self.board_x + width * self.cell_size, pixel_y))
    
    def _draw_stat_panel(self, label: str, value: str, y: int) -> None:
        """Draw a stat panel (score, level, lines)"""
        # Background
        panel_rect = pygame.Rect(self.panel_x, y, 160, 70)
        pygame.draw.rect(self.screen, self.panel_bg, panel_rect)
        pygame.draw.rect(self.screen, self.grid_color, panel_rect, 2)
        
        # Label
        label_text = self.font_small.render(label, True, self.text_gold)
        self.screen.blit(label_text, (self.panel_x + 10, y + 10))
        
        # Value
        value_text = self.font_medium.render(value, True, self.text_color)
        self.screen.blit(value_text, (self.panel_x + 10, y + 35))
    
    def _draw_controls(self) -> None:
        """Draw controls help text"""
        controls_y = self.panel_y + 480
        
        # Background
        panel_rect = pygame.Rect(self.panel_x, controls_y, 160, 140)
        pygame.draw.rect(self.screen, self.panel_bg, panel_rect)
        pygame.draw.rect(self.screen, self.grid_color, panel_rect, 2)
        
        # Title
        title = self.font_small.render(localization.get("ui", "controls"), True, self.text_gold)
        self.screen.blit(title, (self.panel_x + 10, controls_y + 10))
        
        # Controls list based on input method
        if self.use_controller:
            ctrl_section = "controls_controller"
        else:
            ctrl_section = "controls_keyboard"
        
        controls = [
            localization.get(ctrl_section, "move"),
            localization.get(ctrl_section, "rotate_cw"),
            localization.get(ctrl_section, "rotate_ccw"),
            localization.get(ctrl_section, "soft_drop"),
            localization.get(ctrl_section, "hard_drop"),
            localization.get(ctrl_section, "pause"),
        ]
        
        y = controls_y + 40
        for control in controls:
            text = self.font_small.render(control, True, self.text_color)
            # Scale down the font size
            text = pygame.transform.scale(text, (int(text.get_width() * 0.7), 
                                                 int(text.get_height() * 0.7)))
            self.screen.blit(text, (self.panel_x + 10, y))
            y += 16

