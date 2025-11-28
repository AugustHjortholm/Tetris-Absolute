"""
Pygame-based renderer for the Tetris game.
"""

import pygame
from typing import Tuple
from core.interfaces import IRenderer, IBoard, IPiece, IGameState


class PygameRenderer(IRenderer):
    """Pygame implementation of the renderer"""
    
    def __init__(self, screen: pygame.Surface, cell_size: int = 30):
        self.screen = screen
        self.cell_size = cell_size
        
        # Calculate layout
        self.board_x = 20
        self.board_y = 20
        
        # Side panel position
        self.panel_x = self.board_x + 10 * cell_size + 40
        self.panel_y = 20
        
        # Font setup
        pygame.font.init()
        self.font_large = pygame.font.Font(None, 48)
        self.font_medium = pygame.font.Font(None, 36)
        self.font_small = pygame.font.Font(None, 24)
        
        # Colors
        self.bg_color = (20, 20, 40)
        self.grid_color = (40, 40, 60)
        self.text_color = (255, 255, 255)
        self.panel_bg = (30, 30, 50)
    
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
        label = self.font_small.render("NEXT", True, (255, 215, 0))
        self.screen.blit(label, (self.panel_x + 10, self.panel_y + 270))
        
        # Draw the piece centered in the panel
        shape = piece.shape
        small_cell_size = 25
        
        # Calculate centering offset
        piece_width = len(shape[0]) * small_cell_size
        piece_height = len(shape) * small_cell_size
        offset_x = self.panel_x + (160 - piece_width) // 2
        offset_y = self.panel_y + 320 + (120 - piece_height) // 2
        
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
        self._draw_stat_panel("SCORE", str(state.score), y_offset)
        y_offset += 80
        
        # Level
        self._draw_stat_panel("LEVEL", str(state.level), y_offset)
        y_offset += 80
        
        # Lines
        self._draw_stat_panel("LINES", str(state.lines), y_offset)
        
        # Controls (at bottom)
        self._draw_controls()
    
    def render_game_over(self) -> None:
        """Render game over screen"""
        # Semi-transparent overlay
        overlay = pygame.Surface(self.screen.get_size())
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))
        
        # "GAME OVER" text
        game_over_text = self.font_large.render("GAME OVER", True, (255, 0, 0))
        text_rect = game_over_text.get_rect(center=(self.screen.get_width() // 2, 
                                                     self.screen.get_height() // 2 - 30))
        self.screen.blit(game_over_text, text_rect)
        
        # "Press R to restart" text
        restart_text = self.font_small.render("Press R to restart", True, (255, 255, 255))
        restart_rect = restart_text.get_rect(center=(self.screen.get_width() // 2, 
                                                     self.screen.get_height() // 2 + 30))
        self.screen.blit(restart_text, restart_rect)
    
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
        label_text = self.font_small.render(label, True, (255, 215, 0))
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
        title = self.font_small.render("CONTROLS", True, (255, 215, 0))
        self.screen.blit(title, (self.panel_x + 10, controls_y + 10))
        
        # Controls list
        controls = [
            "← → : Move",
            "A D : Rotate L/R",
            "↑ : Soft Drop",
            "↓ : Hard Drop",
            "P : Pause",
            "R : Restart"
        ]
        
        y = controls_y + 40
        for control in controls:
            text = self.font_small.render(control, True, self.text_color)
            # Scale down the font size
            text = pygame.transform.scale(text, (int(text.get_width() * 0.7), 
                                                 int(text.get_height() * 0.7)))
            self.screen.blit(text, (self.panel_x + 10, y))
            y += 16

