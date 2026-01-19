"""
Card Collection Menu - Displays all acquirable cards with filtering and sorting.
"""

import pygame
from typing import List, Optional, Dict, Tuple
from enum import Enum, auto
from config import game_config, localization, cards_config, hex_to_rgb
from core.cards import CardData, CardType, CardManager
from core.card_stats import get_card_stats


class SortMode(Enum):
    """Card sorting modes"""
    ALPHABETICAL = auto()
    BY_COLOR = auto()
    MOST_USED = auto()


class CardCollectionMenu:
    """Menu screen displaying all available cards"""
    
    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.screen_width = screen.get_width()
        self.screen_height = screen.get_height()
        self.running = True
        self.should_return = False

        # Load all cards using a temporary CardManager
        self.card_manager = CardManager(cards_config.all_cards)
        self.all_cards = list(self.card_manager.all_cards.values())

        # Card stats
        self.card_stats = get_card_stats()

        # Filter state (which card types are visible)
        self.type_filters: Dict[CardType, bool] = {
            CardType.BLUE: True,
            CardType.GREEN: True,
            CardType.RED: True,
            CardType.ORANGE: True,
            CardType.GREY: True,
        }

        # Sort mode
        self.sort_mode = SortMode.ALPHABETICAL

        # Scroll state
        self.scroll_offset = 0
        self.max_scroll = 0
        self.is_dragging_scroll = False
        self.scroll_drag_start_y = 0
        self.scroll_drag_offset_start = 0

        # Selection state
        self.selected_card_index = 0
        self.filter_button_selected = -1  # -1 = no filter button, 0-4 = type filters, 5+ = sort buttons
        self.in_filter_row = False  # Whether currently selecting filter/sort buttons

        # Button rectangles for mouse interaction
        self.filter_button_rects = []
        self.sort_button_rects = []
        
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
        
        # Card type colors
        self.type_colors: Dict[CardType, Tuple[int, int, int]] = {}
        for card_type in CardType:
            self.type_colors[card_type] = cards_config.get_card_color(card_type.value, "border")
        
        # Fonts
        pygame.font.init()
        self.title_font = pygame.font.Font(None, 56)
        self.header_font = pygame.font.Font(None, 32)
        self.card_name_font = pygame.font.Font(None, 28)
        self.card_desc_font = pygame.font.Font(None, 22)
        self.small_font = pygame.font.Font(None, 20)
        self.filter_font = pygame.font.Font(None, 24)
        
        # Layout
        self.card_width = 220
        self.card_height = 120
        self.card_spacing = 15
        self.cards_per_row = 3
        self.card_area_top = 160
        self.card_area_left = 40
        self.card_area_height = self.screen_height - self.card_area_top - 60
        
        # Controller support
        self.joystick = None
        if pygame.joystick.get_count() > 0:
            self.joystick = pygame.joystick.Joystick(0)
            self.joystick.init()
        
        # Input cooldown
        self.input_cooldown = 0
        self.cooldown_time = game_config.menu_input_cooldown
        
        # Apply initial sort
        self._update_filtered_cards()
    
    def _get_filtered_cards(self) -> List[CardData]:
        """Get cards filtered by current type filters"""
        filtered = [
            card for card in self.all_cards
            if self.type_filters.get(card.type, True)
        ]
        return filtered
    
    def _sort_cards(self, cards: List[CardData]) -> List[CardData]:
        """Sort cards based on current sort mode"""
        if self.sort_mode == SortMode.ALPHABETICAL:
            return sorted(cards, key=lambda c: c.name.lower())
        elif self.sort_mode == SortMode.BY_COLOR:
            # Sort by type order, then alphabetically within type
            type_order = {
                CardType.BLUE: 0,
                CardType.GREEN: 1,
                CardType.RED: 2,
                CardType.ORANGE: 3,
                CardType.GREY: 4,
            }
            return sorted(cards, key=lambda c: (type_order.get(c.type, 99), c.name.lower()))
        elif self.sort_mode == SortMode.MOST_USED:
            return sorted(
                cards, 
                key=lambda c: self.card_stats.get_selection_count(c.id),
                reverse=True
            )
        return cards
    
    def _update_filtered_cards(self) -> None:
        """Update the displayed cards based on filters and sort"""
        self.displayed_cards = self._sort_cards(self._get_filtered_cards())
        
        # Calculate max scroll
        rows_needed = (len(self.displayed_cards) + self.cards_per_row - 1) // self.cards_per_row
        total_height = rows_needed * (self.card_height + self.card_spacing)
        self.max_scroll = max(0, total_height - self.card_area_height)
        
        # Reset scroll if needed
        if self.scroll_offset > self.max_scroll:
            self.scroll_offset = self.max_scroll
        
        # Reset selection if out of bounds
        if self.selected_card_index >= len(self.displayed_cards):
            self.selected_card_index = max(0, len(self.displayed_cards) - 1)
    
    def _toggle_type_filter(self, card_type: CardType) -> None:
        """Toggle a card type filter"""
        self.type_filters[card_type] = not self.type_filters[card_type]
        
        # Ensure at least one filter is active
        if not any(self.type_filters.values()):
            self.type_filters[card_type] = True
        
        self._update_filtered_cards()
    
    def _set_sort_mode(self, mode: SortMode) -> None:
        """Set the sort mode"""
        self.sort_mode = mode
        self._update_filtered_cards()
    
    def handle_input(self) -> bool:
        """Handle input. Returns False when should exit menu."""
        current_time = pygame.time.get_ticks() / 1000
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return False
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE or event.key == pygame.K_BACKSPACE:
                    self.should_return = True
                    return False
                
                elif event.key == pygame.K_UP:
                    self._navigate_up()
                elif event.key == pygame.K_DOWN:
                    self._navigate_down()
                elif event.key == pygame.K_LEFT:
                    self._navigate_left()
                elif event.key == pygame.K_RIGHT:
                    self._navigate_right()
                elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    self._handle_selection()
            
            elif event.type == pygame.JOYBUTTONDOWN:
                # Circle button - go back
                if event.button == 1:
                    self.should_return = True
                    return False
                # Cross button - select
                elif event.button == 0:
                    self._handle_selection()
                # D-pad
                elif event.button == 11:  # Up
                    self._navigate_up()
                elif event.button == 12:  # Down
                    self._navigate_down()
                elif event.button == 13:  # Left
                    self._navigate_left()
                elif event.button == 14:  # Right
                    self._navigate_right()
            
            elif event.type == pygame.JOYHATMOTION:
                hat_x, hat_y = event.value
                if hat_y > 0:
                    self._navigate_up()
                elif hat_y < 0:
                    self._navigate_down()
                if hat_x < 0:
                    self._navigate_left()
                elif hat_x > 0:
                    self._navigate_right()
            
            elif event.type == pygame.MOUSEWHEEL:
                # Scroll with mouse wheel
                self.scroll_offset -= event.y * 30
                self.scroll_offset = max(0, min(self.scroll_offset, self.max_scroll))

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    self._handle_mouse_click(event.pos)

            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:  # Left click release
                    self.is_dragging_scroll = False

            elif event.type == pygame.MOUSEMOTION:
                if self.is_dragging_scroll:
                    self._handle_scroll_drag(event.pos)
        
        # Controller analog stick
        if self.joystick and current_time > self.input_cooldown:
            axis_y = self.joystick.get_axis(1)
            axis_x = self.joystick.get_axis(0)
            
            if abs(axis_y) > 0.5 or abs(axis_x) > 0.5:
                if axis_y < -0.5:
                    self._navigate_up()
                elif axis_y > 0.5:
                    self._navigate_down()
                if axis_x < -0.5:
                    self._navigate_left()
                elif axis_x > 0.5:
                    self._navigate_right()
                self.input_cooldown = current_time + self.cooldown_time
        
        return True
    
    def _navigate_up(self) -> None:
        """Navigate up"""
        if self.in_filter_row:
            # Go to card area
            self.in_filter_row = False
            self.filter_button_selected = -1
        else:
            # Move up in card grid
            if self.selected_card_index >= self.cards_per_row:
                self.selected_card_index -= self.cards_per_row
                self._ensure_card_visible()
            else:
                # Go to filter row
                self.in_filter_row = True
                self.filter_button_selected = 0
    
    def _navigate_down(self) -> None:
        """Navigate down"""
        if self.in_filter_row:
            # Go to card area
            self.in_filter_row = False
            self.filter_button_selected = -1
        else:
            # Move down in card grid
            new_index = self.selected_card_index + self.cards_per_row
            if new_index < len(self.displayed_cards):
                self.selected_card_index = new_index
                self._ensure_card_visible()
    
    def _navigate_left(self) -> None:
        """Navigate left"""
        if self.in_filter_row:
            if self.filter_button_selected > 0:
                self.filter_button_selected -= 1
        else:
            if self.selected_card_index % self.cards_per_row > 0:
                self.selected_card_index -= 1
    
    def _navigate_right(self) -> None:
        """Navigate right"""
        if self.in_filter_row:
            # 5 type filters + 3 sort buttons = 8 total
            if self.filter_button_selected < 7:
                self.filter_button_selected += 1
        else:
            if (self.selected_card_index % self.cards_per_row < self.cards_per_row - 1 and
                    self.selected_card_index + 1 < len(self.displayed_cards)):
                self.selected_card_index += 1
    
    def _handle_selection(self) -> None:
        """Handle selecting the current item"""
        if self.in_filter_row:
            if 0 <= self.filter_button_selected <= 4:
                # Toggle type filter
                card_types = list(CardType)
                self._toggle_type_filter(card_types[self.filter_button_selected])
            elif self.filter_button_selected == 5:
                self._set_sort_mode(SortMode.ALPHABETICAL)
            elif self.filter_button_selected == 6:
                self._set_sort_mode(SortMode.BY_COLOR)
            elif self.filter_button_selected == 7:
                self._set_sort_mode(SortMode.MOST_USED)
    
    def _handle_mouse_click(self, pos: Tuple[int, int]) -> None:
        """Handle mouse click at position"""
        x, y = pos

        # Check if click is on scroll bar
        bar_x = self.screen_width - 20
        bar_top = self.card_area_top
        bar_height = self.card_area_height
        bar_rect = pygame.Rect(bar_x, bar_top, 8, bar_height)

        if bar_rect.collidepoint(x, y) and self.max_scroll > 0:
            # Start dragging scroll bar
            self.is_dragging_scroll = True
            self.scroll_drag_start_y = y
            self.scroll_drag_offset_start = self.scroll_offset
            return

        # Check filter buttons
        for i, rect in enumerate(self.filter_button_rects):
            if rect.collidepoint(x, y):
                card_types = list(CardType)
                self._toggle_type_filter(card_types[i])
                return

        # Check sort buttons
        for i, rect in enumerate(self.sort_button_rects):
            if rect.collidepoint(x, y):
                sort_modes = [SortMode.ALPHABETICAL, SortMode.BY_COLOR, SortMode.MOST_USED]
                self._set_sort_mode(sort_modes[i])
                return

    def _handle_scroll_drag(self, pos: Tuple[int, int]) -> None:
        """Handle dragging the scroll bar"""
        x, y = pos
        bar_top = self.card_area_top
        bar_height = self.card_area_height

        # Calculate scroll position based on mouse position
        relative_y = y - bar_top
        scroll_ratio = max(0, min(1, relative_y / bar_height))
        self.scroll_offset = int(scroll_ratio * self.max_scroll)
        self.scroll_offset = max(0, min(self.scroll_offset, self.max_scroll))

    def _ensure_card_visible(self) -> None:
        """Ensure the selected card is visible in the scroll area"""
        if not self.displayed_cards:
            return

        row = self.selected_card_index // self.cards_per_row
        card_top = row * (self.card_height + self.card_spacing)
        card_bottom = card_top + self.card_height

        # Scroll up if card is above visible area
        if card_top < self.scroll_offset:
            self.scroll_offset = card_top

        # Scroll down if card is below visible area
        if card_bottom > self.scroll_offset + self.card_area_height:
            self.scroll_offset = card_bottom - self.card_area_height

        # Clamp scroll
        self.scroll_offset = max(0, min(self.scroll_offset, self.max_scroll))
    
    def update(self, dt: float) -> None:
        """Update menu state"""
        pass
    
    def render(self) -> None:
        """Render the card collection menu"""
        self.screen.fill(self.bg_color)
        self._draw_background_grid()
        
        # Title
        title_text = localization.get("collection", "title")
        title_surface = self.title_font.render(title_text, True, self.title_color)
        title_rect = title_surface.get_rect(center=(self.screen_width // 2, 40))
        self.screen.blit(title_surface, title_rect)
        
        # Stats summary
        total_cards = len(self.all_cards)
        cards_used = len([c for c in self.all_cards if self.card_stats.get_selection_count(c.id) > 0])
        total_selections = self.card_stats.get_total_selections()
        
        stats_text = localization.get("collection", "stats_summary").format(
            used=cards_used,
            total=total_cards,
            selections=total_selections
        )
        stats_surface = self.small_font.render(stats_text, True, self.text_color)
        stats_rect = stats_surface.get_rect(center=(self.screen_width // 2, 70))
        self.screen.blit(stats_surface, stats_rect)
        
        # Filter and sort buttons
        self._render_filter_buttons()
        
        # Card display area
        self._render_cards()
        
        # Controls hint
        self._render_controls()
        
        pygame.display.flip()
    
    def _draw_background_grid(self) -> None:
        """Draw subtle grid background"""
        cell_size = game_config.menu_grid_cell_size
        
        for x in range(0, self.screen_width + cell_size, cell_size):
            pygame.draw.line(self.screen, self.grid_color, (x, 0), (x, self.screen_height), 1)
        
        for y in range(0, self.screen_height + cell_size, cell_size):
            pygame.draw.line(self.screen, self.grid_color, (0, y), (self.screen_width, y), 1)
    
    def _render_filter_buttons(self) -> None:
        """Render type filter and sort buttons"""
        y = 100
        start_x = 40
        button_width = 70
        button_height = 28
        spacing = 10

        # Reset button rectangles
        self.filter_button_rects = []
        self.sort_button_rects = []

        # Type filter label
        filter_label = localization.get("collection", "filter_label")
        label_surface = self.filter_font.render(filter_label, True, self.text_color)
        self.screen.blit(label_surface, (start_x, y + 5))

        x = start_x + label_surface.get_width() + 15

        # Type filter buttons
        for i, card_type in enumerate(CardType):
            is_active = self.type_filters[card_type]
            is_selected = self.in_filter_row and self.filter_button_selected == i

            rect = pygame.Rect(x, y, button_width, button_height)
            self.filter_button_rects.append(rect)

            # Button background
            if is_selected:
                bg = self.button_hover
                border = self.selected_color
            elif is_active:
                bg = self.type_colors[card_type]
                border = self.button_border
            else:
                bg = self.button_bg
                border = self.disabled_color

            # Darken if not active
            if not is_active:
                bg = tuple(max(0, c - 50) for c in bg)

            pygame.draw.rect(self.screen, bg, rect, border_radius=4)
            pygame.draw.rect(self.screen, border, rect, 2, border_radius=4)

            # Type name
            type_name = card_type.value.upper()
            text_color = self.text_color if is_active else self.disabled_color
            text_surface = self.small_font.render(type_name, True, text_color)
            text_rect = text_surface.get_rect(center=rect.center)
            self.screen.blit(text_surface, text_rect)

            x += button_width + spacing

        # Separator
        x += 20

        # Sort label
        sort_label = localization.get("collection", "sort_label")
        sort_label_surface = self.filter_font.render(sort_label, True, self.text_color)
        self.screen.blit(sort_label_surface, (x, y + 5))

        x += sort_label_surface.get_width() + 15

        # Sort buttons
        sort_options = [
            (SortMode.ALPHABETICAL, localization.get("collection", "sort_alpha")),
            (SortMode.BY_COLOR, localization.get("collection", "sort_color")),
            (SortMode.MOST_USED, localization.get("collection", "sort_used")),
        ]

        for i, (mode, label) in enumerate(sort_options):
            is_active = self.sort_mode == mode
            is_selected = self.in_filter_row and self.filter_button_selected == 5 + i

            rect = pygame.Rect(x, y, button_width + 10, button_height)
            self.sort_button_rects.append(rect)

            if is_selected:
                bg = self.button_hover
                border = self.selected_color
            elif is_active:
                bg = self.button_hover
                border = self.title_color
            else:
                bg = self.button_bg
                border = self.button_border

            pygame.draw.rect(self.screen, bg, rect, border_radius=4)
            pygame.draw.rect(self.screen, border, rect, 2, border_radius=4)

            text_color = self.title_color if is_active else self.text_color
            text_surface = self.small_font.render(label, True, text_color)
            text_rect = text_surface.get_rect(center=rect.center)
            self.screen.blit(text_surface, text_rect)

            x += button_width + spacing + 10
    
    def _render_cards(self) -> None:
        """Render the card grid"""
        if not self.displayed_cards:
            # No cards message
            no_cards_text = localization.get("collection", "no_cards")
            no_cards_surface = self.header_font.render(no_cards_text, True, self.disabled_color)
            rect = no_cards_surface.get_rect(center=(self.screen_width // 2, self.card_area_top + 100))
            self.screen.blit(no_cards_surface, rect)
            return
        
        # Create clipping rect for card area
        clip_rect = pygame.Rect(
            0, self.card_area_top,
            self.screen_width, self.card_area_height
        )
        self.screen.set_clip(clip_rect)
        
        for i, card in enumerate(self.displayed_cards):
            row = i // self.cards_per_row
            col = i % self.cards_per_row
            
            x = self.card_area_left + col * (self.card_width + self.card_spacing)
            y = self.card_area_top + row * (self.card_height + self.card_spacing) - self.scroll_offset
            
            # Skip if off screen
            if y + self.card_height < self.card_area_top or y > self.card_area_top + self.card_area_height:
                continue
            
            is_selected = (i == self.selected_card_index and not self.in_filter_row)
            self._render_card(card, x, y, is_selected)
        
        # Remove clipping
        self.screen.set_clip(None)
        
        # Draw scroll indicator if needed
        if self.max_scroll > 0:
            self._render_scroll_indicator()
    
    def _render_card(self, card: CardData, x: int, y: int, is_selected: bool) -> None:
        """Render a single card"""
        rect = pygame.Rect(x, y, self.card_width, self.card_height)
        
        # Card background
        type_color = self.type_colors[card.type]
        
        if is_selected:
            bg_color = tuple(min(255, c + 30) for c in type_color)
            border_color = self.selected_color
            border_width = 3
        else:
            bg_color = tuple(c // 3 for c in type_color)  # Darker background
            border_color = type_color
            border_width = 2
        
        pygame.draw.rect(self.screen, bg_color, rect, border_radius=8)
        pygame.draw.rect(self.screen, border_color, rect, border_width, border_radius=8)
        
        # Type indicator bar at top
        type_bar_rect = pygame.Rect(x + 2, y + 2, self.card_width - 4, 6)
        pygame.draw.rect(self.screen, type_color, type_bar_rect, border_radius=3)
        
        # Card name
        name_surface = self.card_name_font.render(card.name, True, self.text_color)
        self.screen.blit(name_surface, (x + 10, y + 14))
        
        # Description (wrapped)
        desc_y = y + 40
        desc_lines = self._wrap_text(card.description, self.card_width - 20, self.card_desc_font)
        for line in desc_lines[:3]:  # Max 3 lines
            desc_surface = self.card_desc_font.render(line, True, self.disabled_color)
            self.screen.blit(desc_surface, (x + 10, desc_y))
            desc_y += 18
        
        # Selection count
        count = self.card_stats.get_selection_count(card.id)
        count_text = localization.get("collection", "times_selected").format(count=count)
        count_surface = self.small_font.render(count_text, True, self.text_color)
        count_rect = count_surface.get_rect(bottomright=(x + self.card_width - 10, y + self.card_height - 8))
        self.screen.blit(count_surface, count_rect)
        
        # Speed change indicator
        if card.speed_change != 0:
            speed_color = (100, 255, 100) if card.speed_change < 0 else (255, 150, 100)
            speed_text = f"+{card.speed_change}" if card.speed_change > 0 else str(card.speed_change)
            speed_surface = self.small_font.render(f"Speed: {speed_text}", True, speed_color)
            self.screen.blit(speed_surface, (x + 10, y + self.card_height - 22))
    
    def _wrap_text(self, text: str, max_width: int, font: pygame.font.Font) -> List[str]:
        """Wrap text to fit within a given width"""
        words = text.split(' ')
        lines = []
        current_line = []
        
        for word in words:
            current_line.append(word)
            test_line = ' '.join(current_line)
            if font.size(test_line)[0] > max_width:
                if len(current_line) > 1:
                    current_line.pop()
                    lines.append(' '.join(current_line))
                    current_line = [word]
                else:
                    lines.append(word)
                    current_line = []
        
        if current_line:
            lines.append(' '.join(current_line))
        
        return lines
    
    def _render_scroll_indicator(self) -> None:
        """Render a scroll indicator on the right side"""
        bar_x = self.screen_width - 20
        bar_top = self.card_area_top
        bar_height = self.card_area_height
        
        # Background track
        pygame.draw.rect(
            self.screen, 
            self.grid_color,
            (bar_x, bar_top, 8, bar_height),
            border_radius=4
        )
        
        # Scrollbar thumb
        if self.max_scroll > 0:
            visible_ratio = self.card_area_height / (self.max_scroll + self.card_area_height)
            thumb_height = max(30, int(bar_height * visible_ratio))
            scroll_ratio = self.scroll_offset / self.max_scroll if self.max_scroll > 0 else 0
            thumb_y = bar_top + int((bar_height - thumb_height) * scroll_ratio)
            
            pygame.draw.rect(
                self.screen,
                self.button_border,
                (bar_x, thumb_y, 8, thumb_height),
                border_radius=4
            )
    
    def _render_controls(self) -> None:
        """Render control hints at bottom"""
        y = self.screen_height - 35
        
        if self.joystick:
            controls = localization.get("collection", "controls_controller")
        else:
            controls = localization.get("collection", "controls_keyboard")
        
        controls_surface = self.small_font.render(controls, True, self.disabled_color)
        controls_rect = controls_surface.get_rect(center=(self.screen_width // 2, y))
        self.screen.blit(controls_surface, controls_rect)
    
    def run(self) -> bool:
        """Run the menu loop. Returns True if should go back to main menu."""
        clock = pygame.time.Clock()
        
        while self.running and not self.should_return:
            dt = clock.tick(60) / 1000
            
            if not self.handle_input():
                break
            
            self.update(dt)
            self.render()
        
        return True
