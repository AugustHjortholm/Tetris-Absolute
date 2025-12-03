"""
Main menu screen for Tetris Roguelike.
Colors and settings loaded from config/game_config.json
"""

import pygame
from typing import List, Optional, Callable
from enum import Enum, auto
from config import game_config, localization


class MenuState(Enum):
    """Menu states"""
    MAIN_MENU = auto()
    IN_GAME = auto()
    CUSTOM_GAME = auto()
    CHALLENGES = auto()
    OPTIONS = auto()


class MenuItem:
    """Represents a menu button"""
    
    def __init__(self, text: str, action: Optional[Callable] = None, enabled: bool = True):
        self.text = text
        self.action = action
        self.enabled = enabled
        self.rect: Optional[pygame.Rect] = None


class MainMenu:
    """Main menu screen"""
    
    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.running = True
        self.selected_index = 0
        self.state = MenuState.MAIN_MENU
        
        # Colors from config
        self.bg_color = game_config.get_menu_color("background")
        self.title_color = game_config.get_menu_color("title")
        self.text_color = game_config.get_menu_color("text")
        self.selected_color = game_config.get_menu_color("selected")
        self.disabled_color = game_config.get_menu_color("disabled")
        self.button_bg = game_config.get_menu_color("button_background")
        self.button_hover = game_config.get_menu_color("button_hover")
        self.button_border = game_config.get_menu_color("button_border")
        self.grid_color = game_config.get_menu_color("grid_line")
        self.grid_highlight = game_config.get_menu_color("grid_highlight")
        
        # Grid settings from config
        self.grid_cell_size = game_config.menu_grid_cell_size
        
        # Fonts
        pygame.font.init()
        self.title_font = pygame.font.Font(None, 96)
        self.subtitle_font = pygame.font.Font(None, 36)
        self.menu_font = pygame.font.Font(None, 48)
        self.small_font = pygame.font.Font(None, 24)
        
        # Menu items with localized text
        self.menu_items: List[MenuItem] = [
            MenuItem(localization.get("menu", "new_game"), self._start_new_game, True),
            MenuItem(localization.get("menu", "custom_game"), self._custom_game, False),
            MenuItem(localization.get("menu", "challenges"), self._challenges, False),
            MenuItem(localization.get("menu", "options"), self._options, False),
            MenuItem(localization.get("menu", "exit"), self._exit_game, True),
        ]
        
        # Animation
        self.animation_time = 0
        
        # Controller support
        self.joystick = None
        if pygame.joystick.get_count() > 0:
            self.joystick = pygame.joystick.Joystick(0)
            self.joystick.init()
        
        # Input cooldown for controller (from config)
        self.input_cooldown = 0
        self.cooldown_time = game_config.menu_input_cooldown
    
    def _start_new_game(self):
        """Start a new game"""
        self.state = MenuState.IN_GAME
    
    def _custom_game(self):
        """Custom game - not implemented"""
        pass
    
    def _challenges(self):
        """Challenges - not implemented"""
        pass
    
    def _options(self):
        """Options - not implemented"""
        pass
    
    def _exit_game(self):
        """Exit the game"""
        self.running = False
    
    def handle_input(self) -> bool:
        """Handle menu input. Returns False if should quit."""
        current_time = pygame.time.get_ticks() / 1000
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return False
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self._move_selection(-1)
                elif event.key == pygame.K_DOWN:
                    self._move_selection(1)
                elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    self._select_current()
                elif event.key == pygame.K_ESCAPE:
                    self.running = False
                    return False
            
            elif event.type == pygame.JOYBUTTONDOWN:
                # D-pad up
                if event.button == 11:  # PS D-pad up
                    self._move_selection(-1)
                # D-pad down
                elif event.button == 12:  # PS D-pad down
                    self._move_selection(1)
                # Cross (confirm)
                elif event.button == 0:
                    self._select_current()
            
            elif event.type == pygame.JOYHATMOTION:
                hat_x, hat_y = event.value
                if hat_y > 0:  # Up
                    self._move_selection(-1)
                elif hat_y < 0:  # Down
                    self._move_selection(1)
            
            elif event.type == pygame.MOUSEMOTION:
                self._handle_mouse_hover(event.pos)
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    self._handle_mouse_click(event.pos)
        
        # Controller analog stick (with cooldown)
        if self.joystick and current_time > self.input_cooldown:
            axis_y = self.joystick.get_axis(1)  # Left stick Y
            if axis_y < -0.5:
                self._move_selection(-1)
                self.input_cooldown = current_time + self.cooldown_time
            elif axis_y > 0.5:
                self._move_selection(1)
                self.input_cooldown = current_time + self.cooldown_time
        
        return True
    
    def _move_selection(self, direction: int):
        """Move menu selection up or down"""
        new_index = self.selected_index + direction
        
        # Wrap around
        if new_index < 0:
            new_index = len(self.menu_items) - 1
        elif new_index >= len(self.menu_items):
            new_index = 0
        
        self.selected_index = new_index
    
    def _select_current(self):
        """Select the current menu item"""
        item = self.menu_items[self.selected_index]
        if item.enabled and item.action:
            item.action()
    
    def _handle_mouse_hover(self, pos):
        """Handle mouse hover over menu items"""
        for i, item in enumerate(self.menu_items):
            if item.rect and item.rect.collidepoint(pos):
                self.selected_index = i
                break
    
    def _handle_mouse_click(self, pos):
        """Handle mouse click on menu items"""
        for i, item in enumerate(self.menu_items):
            if item.rect and item.rect.collidepoint(pos) and item.enabled:
                self.selected_index = i
                self._select_current()
                break
    
    def update(self, dt: float):
        """Update menu animations"""
        self.animation_time += dt
    
    def render(self):
        """Render the menu"""
        # Background with gradient effect
        self.screen.fill(self.bg_color)
        self._draw_background_effects()
        
        screen_width = self.screen.get_width()
        screen_height = self.screen.get_height()
        
        # Title from localization
        title_text = localization.get("game", "title")
        title_surface = self.title_font.render(title_text, True, self.title_color)
        title_rect = title_surface.get_rect(center=(screen_width // 2, 100))
        self.screen.blit(title_surface, title_rect)
        
        # Subtitle from localization
        subtitle_text = localization.get("game", "subtitle")
        subtitle_surface = self.subtitle_font.render(subtitle_text, True, self.text_color)
        subtitle_rect = subtitle_surface.get_rect(center=(screen_width // 2, 150))
        self.screen.blit(subtitle_surface, subtitle_rect)
        
        # Menu items
        menu_start_y = 250
        menu_spacing = 70
        button_width = 300
        button_height = 55
        
        for i, item in enumerate(self.menu_items):
            y = menu_start_y + i * menu_spacing
            x = (screen_width - button_width) // 2
            
            # Store rect for mouse interaction
            item.rect = pygame.Rect(x, y, button_width, button_height)
            
            # Determine colors
            is_selected = i == self.selected_index
            
            if not item.enabled:
                text_color = self.disabled_color
                bg_color = self.button_bg
                border_color = self.disabled_color
            elif is_selected:
                text_color = self.selected_color
                bg_color = self.button_hover
                border_color = self.selected_color
            else:
                text_color = self.text_color
                bg_color = self.button_bg
                border_color = self.button_border
            
            # Draw button background
            pygame.draw.rect(self.screen, bg_color, item.rect, border_radius=8)
            pygame.draw.rect(self.screen, border_color, item.rect, 2, border_radius=8)
            
            # Draw selection indicator
            if is_selected and item.enabled:
                # Animated arrow
                arrow_offset = int(5 * abs(pygame.math.Vector2(1, 0).rotate(self.animation_time * 360).x))
                arrow_x = x - 30 - arrow_offset
                arrow_text = self.menu_font.render(">", True, self.selected_color)
                self.screen.blit(arrow_text, (arrow_x, y + 8))
            
            # Draw text
            text_surface = self.menu_font.render(item.text, True, text_color)
            text_rect = text_surface.get_rect(center=item.rect.center)
            self.screen.blit(text_surface, text_rect)
            
            # "Coming Soon" for disabled items (localized)
            if not item.enabled:
                soon_text = self.small_font.render(
                    localization.get("menu", "coming_soon"), 
                    True, 
                    self.disabled_color
                )
                soon_rect = soon_text.get_rect(center=(item.rect.centerx, item.rect.bottom + 12))
                self.screen.blit(soon_text, soon_rect)
        
        # Controls hint at bottom (localized)
        controls_y = screen_height - 50
        if self.joystick:
            controls_text = localization.get("menu", "controls_controller")
        else:
            controls_text = localization.get("menu", "controls_keyboard")
        
        controls_surface = self.small_font.render(controls_text, True, self.disabled_color)
        controls_rect = controls_surface.get_rect(center=(screen_width // 2, controls_y))
        self.screen.blit(controls_surface, controls_rect)
        
        # Version from config
        version_text = game_config.menu_version
        version_surface = self.small_font.render(version_text, True, self.disabled_color)
        self.screen.blit(version_surface, (10, screen_height - 25))
        
        pygame.display.flip()
    
    def _draw_background_effects(self):
        """Draw a subtle grid background similar to the game board"""
        screen_width = self.screen.get_width()
        screen_height = self.screen.get_height()
        
        # Grid cell size from config
        cell_size = self.grid_cell_size
        
        # Draw vertical lines
        for x in range(0, screen_width + cell_size, cell_size):
            pygame.draw.line(self.screen, self.grid_color, (x, 0), (x, screen_height), 1)
        
        # Draw horizontal lines
        for y in range(0, screen_height + cell_size, cell_size):
            pygame.draw.line(self.screen, self.grid_color, (0, y), (screen_width, y), 1)
        
        # Draw slightly brighter cell borders for depth
        for x in range(0, screen_width, cell_size):
            for y in range(0, screen_height, cell_size):
                # Inner highlight on some cells for subtle variation
                if (x // cell_size + y // cell_size) % 3 == 0:
                    inner_rect = pygame.Rect(x + 2, y + 2, cell_size - 4, cell_size - 4)
                    pygame.draw.rect(self.screen, self.grid_highlight, inner_rect, 1)
    
    def run(self) -> MenuState:
        """Run the menu loop. Returns the state when exiting."""
        clock = pygame.time.Clock()
        
        while self.running and self.state == MenuState.MAIN_MENU:
            dt = clock.tick(60) / 1000  # Delta time in seconds
            
            if not self.handle_input():
                return MenuState.MAIN_MENU  # Quit requested
            
            self.update(dt)
            self.render()
        
        return self.state

