"""
Card selection UI renderer.
Renders cards for the roguelike card selection screen.
"""

import pygame
from typing import List, Tuple, Optional
from core.cards import CardData, CardType, CardManager
from config import cards_config, localization


class CardRenderer:
    """Renders the card selection screen"""
    
    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.screen_width = screen.get_width()
        self.screen_height = screen.get_height()
        
        # Card dimensions
        self.card_width = 180
        self.card_height = 280
        self.card_spacing = 30
        self.border_width = 3
        
        # Calculate positions for 3 cards
        total_width = 3 * self.card_width + 2 * self.card_spacing
        self.start_x = (self.screen_width - total_width) // 2
        self.card_y = (self.screen_height - self.card_height) // 2 - 20
        
        # Fonts
        pygame.font.init()
        self.title_font = pygame.font.Font(None, 48)
        self.card_name_font = pygame.font.Font(None, 28)
        self.card_desc_font = pygame.font.Font(None, 20)
        self.speed_font = pygame.font.Font(None, 24)
        self.stack_font = pygame.font.Font(None, 18)
        self.block_size = 16  # Size of blocks when rendering piece preview
        
        # Selection state
        self.selected_index = 0
        self.hover_animation = 0
        
    def _get_card_colors(self, card_type: CardType) -> dict:
        """Get colors for a card type"""
        type_str = card_type.value
        return {
            "background": cards_config.get_card_color(type_str, "background"),
            "border": cards_config.get_card_color(type_str, "border"),
            "text": cards_config.get_card_color(type_str, "text"),
            "highlight": cards_config.get_card_color(type_str, "highlight")
        }
    
    def _render_piece_preview(self, surface: pygame.Surface, shape: List[List[int]], 
                               color: Tuple[int, int, int], x: int, y: int) -> int:
        """Render a piece shape preview on the card. Returns block count."""
        if not shape:
            return 0
        
        block_count = 0
        
        # Calculate centering
        shape_width = len(shape[0]) * self.block_size
        shape_height = len(shape) * self.block_size
        
        start_x = x - shape_width // 2
        start_y = y
        
        for row_idx, row in enumerate(shape):
            for col_idx, cell in enumerate(row):
                if cell:
                    block_count += 1
                    rect = pygame.Rect(
                        start_x + col_idx * self.block_size,
                        start_y + row_idx * self.block_size,
                        self.block_size - 1,
                        self.block_size - 1
                    )
                    pygame.draw.rect(surface, color, rect)
                    # Add highlight
                    pygame.draw.line(surface, self._lighten_color(color), 
                                   (rect.left, rect.top), (rect.right, rect.top))
                    pygame.draw.line(surface, self._lighten_color(color),
                                   (rect.left, rect.top), (rect.left, rect.bottom))
        
        return block_count
    
    def _lighten_color(self, color: Tuple[int, int, int]) -> Tuple[int, int, int]:
        """Lighten a color for highlights"""
        return tuple(min(255, c + 60) for c in color)
    
    def _darken_color(self, color: Tuple[int, int, int]) -> Tuple[int, int, int]:
        """Darken a color for shadows"""
        return tuple(max(0, c - 40) for c in color)
    
    def _hex_to_rgb(self, hex_color: str) -> Tuple[int, int, int]:
        """Convert hex color to RGB"""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    def render_card(self, card: CardData, x: int, y: int, selected: bool = False,
                    collected_count: int = 0) -> pygame.Rect:
        """Render a single card. Returns the card rect."""
        colors = self._get_card_colors(card.type)
        
        # Card background
        card_rect = pygame.Rect(x, y, self.card_width, self.card_height)
        
        # Hover/selection effect
        if selected:
            # Draw glow effect
            glow_rect = card_rect.inflate(10, 10)
            glow_surface = pygame.Surface((glow_rect.width, glow_rect.height), pygame.SRCALPHA)
            pygame.draw.rect(glow_surface, (*colors["highlight"], 100), glow_surface.get_rect(), border_radius=12)
            self.screen.blit(glow_surface, glow_rect.topleft)
            
            # Move card up slightly when selected
            card_rect.y -= 10
        
        # Draw card background
        pygame.draw.rect(self.screen, colors["background"], card_rect, border_radius=8)
        
        # Draw border
        border_color = colors["highlight"] if selected else colors["border"]
        pygame.draw.rect(self.screen, border_color, card_rect, self.border_width, border_radius=8)
        
        # Card type indicator (top banner)
        banner_rect = pygame.Rect(card_rect.x, card_rect.y, self.card_width, 30)
        banner_color = colors["border"]
        pygame.draw.rect(self.screen, banner_color, banner_rect, border_radius=8)
        pygame.draw.rect(self.screen, colors["background"], 
                        pygame.Rect(card_rect.x, card_rect.y + 15, self.card_width, 15))
        
        # Card type text
        type_text = card.type.value.upper()
        type_surface = self.stack_font.render(type_text, True, colors["text"])
        type_rect = type_surface.get_rect(center=(card_rect.centerx, card_rect.y + 15))
        self.screen.blit(type_surface, type_rect)
        
        # Card name
        name_surface = self.card_name_font.render(card.name, True, colors["text"])
        name_rect = name_surface.get_rect(center=(card_rect.centerx, card_rect.y + 50))
        self.screen.blit(name_surface, name_rect)
        
        # Content area - depends on card type
        content_y = card_rect.y + 75
        
        if card.type == CardType.BLUE and card.piece_shape:
            # Render piece preview for blue cards
            piece_color = self._hex_to_rgb(card.piece_color) if card.piece_color else (255, 255, 255)
            block_count = self._render_piece_preview(
                self.screen, card.piece_shape, piece_color,
                card_rect.centerx, content_y
            )
            
            # Show block count
            count_text = f"{block_count} blocks"
            count_surface = self.stack_font.render(count_text, True, colors["text"])
            count_rect = count_surface.get_rect(center=(card_rect.centerx, content_y + 80))
            self.screen.blit(count_surface, count_rect)
            
            content_y += 100
        else:
            # For other cards, add some spacing
            content_y += 20
        
        # Description (word wrap)
        self._render_wrapped_text(
            card.description, 
            card_rect.x + 10, content_y,
            self.card_width - 20, colors["text"]
        )
        
        # Stack indicator if applicable
        if card.stackable and card.max_stack > 1:
            stack_text = f"Stack: {collected_count}/{card.max_stack}"
            stack_surface = self.stack_font.render(stack_text, True, colors["highlight"])
            stack_rect = stack_surface.get_rect(
                center=(card_rect.centerx, card_rect.bottom - 55)
            )
            self.screen.blit(stack_surface, stack_rect)
        
        # Speed change indicator (bottom left)
        speed_text = self._format_speed_change(card.speed_change)
        speed_color = (100, 255, 100) if card.speed_change < 0 else (255, 100, 100) if card.speed_change > 0 else (200, 200, 200)
        speed_surface = self.speed_font.render(speed_text, True, speed_color)
        speed_rect = speed_surface.get_rect(bottomleft=(card_rect.x + 10, card_rect.bottom - 10))
        self.screen.blit(speed_surface, speed_rect)
        
        # Speed label
        label_surface = self.stack_font.render("Speed", True, (150, 150, 150))
        label_rect = label_surface.get_rect(bottomleft=(card_rect.x + 10, speed_rect.top - 2))
        self.screen.blit(label_surface, label_rect)
        
        return card_rect
    
    def _format_speed_change(self, speed: int) -> str:
        """Format speed change for display"""
        if speed > 0:
            return f"+{speed}"
        elif speed < 0:
            return str(speed)
        return "0"
    
    def _render_wrapped_text(self, text: str, x: int, y: int, max_width: int,
                              color: Tuple[int, int, int]) -> None:
        """Render text with word wrapping"""
        words = text.split(' ')
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            test_surface = self.card_desc_font.render(test_line, True, color)
            
            if test_surface.get_width() <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
        
        if current_line:
            lines.append(' '.join(current_line))
        
        line_height = self.card_desc_font.get_height() + 2
        for i, line in enumerate(lines):
            line_surface = self.card_desc_font.render(line, True, color)
            line_rect = line_surface.get_rect(centerx=x + max_width // 2, top=y + i * line_height)
            self.screen.blit(line_surface, line_rect)
    
    def render_selection_screen(self, cards: List[CardData], card_manager: CardManager,
                                 current_speed: int) -> None:
        """Render the full card selection screen"""
        # Dim background
        overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        self.screen.blit(overlay, (0, 0))
        
        # Title
        title_text = "CHOOSE YOUR CARD"
        title_surface = self.title_font.render(title_text, True, (255, 215, 0))
        title_rect = title_surface.get_rect(center=(self.screen_width // 2, 50))
        self.screen.blit(title_surface, title_rect)
        
        # Current speed level
        speed_text = f"Current Speed Level: {current_speed}"
        speed_surface = self.card_desc_font.render(speed_text, True, (200, 200, 200))
        speed_rect = speed_surface.get_rect(center=(self.screen_width // 2, 85))
        self.screen.blit(speed_surface, speed_rect)
        
        # Render cards
        for i, card in enumerate(cards):
            x = self.start_x + i * (self.card_width + self.card_spacing)
            collected = card_manager.get_collected_count(card.id)
            self.render_card(card, x, self.card_y, selected=(i == self.selected_index),
                           collected_count=collected)
        
        # Instructions
        instructions = "Use Left/Right to select, Enter/Space to confirm"
        inst_surface = self.card_desc_font.render(instructions, True, (150, 150, 150))
        inst_rect = inst_surface.get_rect(center=(self.screen_width // 2, self.screen_height - 40))
        self.screen.blit(inst_surface, inst_rect)
        
        # Controller instructions
        ctrl_text = "Controller: D-Pad to select, Cross to confirm"
        ctrl_surface = self.card_desc_font.render(ctrl_text, True, (150, 150, 150))
        ctrl_rect = ctrl_surface.get_rect(center=(self.screen_width // 2, self.screen_height - 20))
        self.screen.blit(ctrl_surface, ctrl_rect)
    
    def render_removal_screen(self, cards: List[CardData], card_manager: CardManager,
                              remaining_removals: int) -> None:
        """Render the card removal selection screen"""
        # Dim background
        overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        self.screen.blit(overlay, (0, 0))
        
        # Title
        title_text = "CHOOSE A CARD TO REMOVE"
        title_surface = self.title_font.render(title_text, True, (255, 100, 100))
        title_rect = title_surface.get_rect(center=(self.screen_width // 2, 50))
        self.screen.blit(title_surface, title_rect)
        
        # Remaining removals
        remain_text = f"Removals remaining: {remaining_removals}"
        remain_surface = self.card_desc_font.render(remain_text, True, (200, 200, 200))
        remain_rect = remain_surface.get_rect(center=(self.screen_width // 2, 85))
        self.screen.blit(remain_surface, remain_rect)
        
        # Calculate card layout - may need more or fewer columns
        max_cards_per_row = 4
        num_cards = len(cards)
        cards_per_row = min(num_cards, max_cards_per_row)
        
        # Smaller cards for removal screen
        small_card_width = 140
        small_card_height = 200
        small_spacing = 20
        
        total_width = cards_per_row * small_card_width + (cards_per_row - 1) * small_spacing
        start_x = (self.screen_width - total_width) // 2
        
        # Render cards in grid
        for i, card in enumerate(cards):
            row = i // max_cards_per_row
            col = i % max_cards_per_row
            
            # Center partial rows
            cards_in_row = min(max_cards_per_row, num_cards - row * max_cards_per_row)
            row_width = cards_in_row * small_card_width + (cards_in_row - 1) * small_spacing
            row_start_x = (self.screen_width - row_width) // 2
            
            x = row_start_x + col * (small_card_width + small_spacing)
            y = 120 + row * (small_card_height + small_spacing)
            
            self._render_removal_card(card, x, y, small_card_width, small_card_height,
                                      selected=(i == self.selected_index))
        
        # Instructions
        instructions = "Select a card to REMOVE its effect"
        inst_surface = self.card_desc_font.render(instructions, True, (255, 150, 150))
        inst_rect = inst_surface.get_rect(center=(self.screen_width // 2, self.screen_height - 40))
        self.screen.blit(inst_surface, inst_rect)
    
    def _render_removal_card(self, card: CardData, x: int, y: int, 
                              width: int, height: int, selected: bool) -> None:
        """Render a card for the removal screen"""
        colors = self._get_card_colors(card.type)
        
        card_rect = pygame.Rect(x, y, width, height)
        
        # Selection effect
        if selected:
            # Red glow for removal
            glow_rect = card_rect.inflate(8, 8)
            glow_surface = pygame.Surface((glow_rect.width, glow_rect.height), pygame.SRCALPHA)
            pygame.draw.rect(glow_surface, (255, 100, 100, 150), glow_surface.get_rect(), border_radius=10)
            self.screen.blit(glow_surface, glow_rect.topleft)
            card_rect.y -= 5
        
        # Draw card background
        pygame.draw.rect(self.screen, colors["background"], card_rect, border_radius=6)
        
        # Draw border (red if selected)
        border_color = (255, 100, 100) if selected else colors["border"]
        pygame.draw.rect(self.screen, border_color, card_rect, 2, border_radius=6)
        
        # Card name
        name_surface = self.card_desc_font.render(card.name, True, colors["text"])
        name_rect = name_surface.get_rect(centerx=card_rect.centerx, top=card_rect.top + 10)
        self.screen.blit(name_surface, name_rect)
        
        # Card type
        type_text = card.type.value.upper()
        type_surface = self.stack_font.render(type_text, True, colors["border"])
        type_rect = type_surface.get_rect(centerx=card_rect.centerx, top=card_rect.top + 35)
        self.screen.blit(type_surface, type_rect)
        
        # Description (abbreviated)
        desc = card.description[:30] + "..." if len(card.description) > 30 else card.description
        desc_surface = self.stack_font.render(desc, True, colors["text"])
        desc_rect = desc_surface.get_rect(centerx=card_rect.centerx, bottom=card_rect.bottom - 10)
        self.screen.blit(desc_surface, desc_rect)
    
    def select_next(self, cards: List[CardData]) -> None:
        """Move selection to next card"""
        if cards:
            self.selected_index = (self.selected_index + 1) % len(cards)
    
    def select_prev(self, cards: List[CardData]) -> None:
        """Move selection to previous card"""
        if cards:
            self.selected_index = (self.selected_index - 1) % len(cards)
    
    def get_selected_card(self, cards: List[CardData]) -> Optional[CardData]:
        """Get the currently selected card"""
        if cards and 0 <= self.selected_index < len(cards):
            return cards[self.selected_index]
        return None
    
    def reset_selection(self) -> None:
        """Reset selection to first card"""
        self.selected_index = 0

