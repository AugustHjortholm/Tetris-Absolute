"""
Card effect implementations.
Each effect type has its own class that handles applying and removing effects.
"""

from typing import TYPE_CHECKING, Dict, Any, List, Optional
from core.cards import CardEffect, CardEffectRegistry, CardData, CardType

if TYPE_CHECKING:
    from game import Game


class GameModifiers:
    """Tracks all active game modifiers from cards"""
    
    def __init__(self):
        self.reset()
    
    def reset(self):
        """Reset all modifiers"""
        # Scoring modifiers
        self.tetris_bonus = 0.0
        self.b2b_bonus = 0.0
        self.combo_bonuses: List[Dict[str, Any]] = []  # [{min_combo, bonus}]
        self.line_bonus = 0
        self.hard_drop_bonus = 0
        self.double_bonus = 0
        self.triple_bonus = 0
        self.score_multiplier = 1.0
        
        # Gameplay modifiers
        self.frozen_lines: List[int] = []  # Row indices that can't be cleared
        self.hold_disabled = False
        self.ghost_disabled = False
        self.lock_delay_multiplier = 1.0
        self.random_hole_frequency = 0  # 0 = disabled
        self.pieces_since_hole = 0
        self.filled_columns: List[int] = []  # Column indices that are filled
        self.removed_piece_types: List[str] = []  # Piece types removed from bag
        
        # Extra pieces added by blue cards
        self.extra_pieces: List[Dict[str, Any]] = []  # [{id, shape, color}]
        
        # Card tracking
        self.cards_collected: List[str] = []  # List of card IDs in order
        self.last_card_id: Optional[str] = None
    
    def get_total_combo_bonus(self, combo_count: int) -> float:
        """Calculate total combo bonus multiplier for a given combo count"""
        total = 0.0
        for bonus in self.combo_bonuses:
            if combo_count >= bonus["min_combo"]:
                total += bonus["multiplier_bonus"]
        return total
    
    def calculate_final_score(self, base_score: int, lines_cleared: int, 
                               is_tetris: bool, is_b2b: bool, combo_count: int,
                               hard_drop_distance: int = 0) -> int:
        """Calculate final score with all modifiers applied"""
        score = base_score
        
        # Line bonuses
        score += lines_cleared * self.line_bonus
        
        # Line type bonuses
        if lines_cleared == 2:
            score += self.double_bonus
        elif lines_cleared == 3:
            score += self.triple_bonus
        
        # Hard drop bonus
        score += hard_drop_distance * self.hard_drop_bonus
        
        # Tetris bonus
        if is_tetris:
            score = int(score * (1 + self.tetris_bonus))
        
        # Back-to-back bonus
        if is_b2b:
            score = int(score * (1 + self.b2b_bonus))
        
        # Combo bonus
        if combo_count >= 2:
            combo_bonus = self.get_total_combo_bonus(combo_count)
            score = int(score * (1 + combo_bonus))
        
        # Global score multiplier
        score = int(score * self.score_multiplier)
        
        return score


# Global modifiers instance - will be set per game
_active_modifiers: Optional[GameModifiers] = None


def get_modifiers() -> GameModifiers:
    """Get the current game modifiers"""
    global _active_modifiers
    if _active_modifiers is None:
        _active_modifiers = GameModifiers()
    return _active_modifiers


def set_modifiers(modifiers: GameModifiers) -> None:
    """Set the active modifiers"""
    global _active_modifiers
    _active_modifiers = modifiers


# ============ Blue Card Effects - New Pieces ============

@CardEffectRegistry.register("add_piece")
class AddPieceEffect(CardEffect):
    """Adds a new piece type to the game"""
    
    def __init__(self, piece_id: str, shape: List[List[int]], color: str):
        self.piece_id = piece_id
        self.shape = shape
        self.color = color
    
    def _hex_to_rgb(self, hex_color: str) -> tuple:
        """Convert hex color to RGB tuple"""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    def apply(self, game: 'Game') -> None:
        from implementations.standard_piece import PieceFactory
        
        modifiers = get_modifiers()
        modifiers.extra_pieces.append({
            "id": self.piece_id,
            "shape": self.shape,
            "color": self.color
        })
        
        # Register with piece factory
        color_rgb = self._hex_to_rgb(self.color)
        PieceFactory.register_custom_piece(self.piece_id, self.shape, color_rgb)
        
        # Add to piece generator
        if hasattr(game.piece_generator, 'add_extra_piece'):
            game.piece_generator.add_extra_piece(self.piece_id, self.shape, self.color)
        
        # Inject this piece as the next piece so player gets it immediately
        if hasattr(game.piece_generator, 'inject_next_piece'):
            game.piece_generator.inject_next_piece(self.piece_id)
    
    def remove(self, game: 'Game') -> None:
        modifiers = get_modifiers()
        modifiers.extra_pieces = [p for p in modifiers.extra_pieces 
                                   if p["id"] != self.piece_id]
    
    def get_description(self) -> str:
        return f"Added piece: {self.piece_id}"


# ============ Green Card Effects - Bonuses ============

@CardEffectRegistry.register("combo_bonus")
class ComboBonusEffect(CardEffect):
    """Adds combo bonus multiplier"""
    
    def __init__(self, min_combo: int, multiplier_bonus: float):
        self.min_combo = min_combo
        self.multiplier_bonus = multiplier_bonus
    
    def apply(self, game: 'Game') -> None:
        modifiers = get_modifiers()
        modifiers.combo_bonuses.append({
            "min_combo": self.min_combo,
            "multiplier_bonus": self.multiplier_bonus
        })
    
    def remove(self, game: 'Game') -> None:
        modifiers = get_modifiers()
        # Remove one matching bonus
        for i, bonus in enumerate(modifiers.combo_bonuses):
            if (bonus["min_combo"] == self.min_combo and 
                bonus["multiplier_bonus"] == self.multiplier_bonus):
                modifiers.combo_bonuses.pop(i)
                break
    
    def get_description(self) -> str:
        return f"+{self.multiplier_bonus}x at {self.min_combo}+ combo"


@CardEffectRegistry.register("tetris_bonus")
class TetrisBonusEffect(CardEffect):
    """Increases Tetris multiplier"""
    
    def __init__(self, bonus: float):
        self.bonus = bonus
    
    def apply(self, game: 'Game') -> None:
        get_modifiers().tetris_bonus += self.bonus
    
    def remove(self, game: 'Game') -> None:
        get_modifiers().tetris_bonus -= self.bonus
    
    def get_description(self) -> str:
        return f"+{self.bonus}x Tetris bonus"


@CardEffectRegistry.register("b2b_bonus")
class B2BBonusEffect(CardEffect):
    """Increases Back-to-Back multiplier"""
    
    def __init__(self, bonus: float):
        self.bonus = bonus
    
    def apply(self, game: 'Game') -> None:
        get_modifiers().b2b_bonus += self.bonus
    
    def remove(self, game: 'Game') -> None:
        get_modifiers().b2b_bonus -= self.bonus
    
    def get_description(self) -> str:
        return f"+{self.bonus}x Back-to-Back bonus"


@CardEffectRegistry.register("line_bonus")
class LineBonusEffect(CardEffect):
    """Adds bonus points per line cleared"""
    
    def __init__(self, bonus: int):
        self.bonus = bonus
    
    def apply(self, game: 'Game') -> None:
        get_modifiers().line_bonus += self.bonus
    
    def remove(self, game: 'Game') -> None:
        get_modifiers().line_bonus -= self.bonus
    
    def get_description(self) -> str:
        return f"+{self.bonus} points per line"


@CardEffectRegistry.register("hard_drop_bonus")
class HardDropBonusEffect(CardEffect):
    """Adds bonus points for hard drop distance"""
    
    def __init__(self, bonus: int):
        self.bonus = bonus
    
    def apply(self, game: 'Game') -> None:
        get_modifiers().hard_drop_bonus += self.bonus
    
    def remove(self, game: 'Game') -> None:
        get_modifiers().hard_drop_bonus -= self.bonus
    
    def get_description(self) -> str:
        return f"+{self.bonus} points per hard drop cell"


@CardEffectRegistry.register("double_bonus")
class DoubleBonusEffect(CardEffect):
    """Adds bonus points for double line clears"""
    
    def __init__(self, bonus: int):
        self.bonus = bonus
    
    def apply(self, game: 'Game') -> None:
        get_modifiers().double_bonus += self.bonus
    
    def remove(self, game: 'Game') -> None:
        get_modifiers().double_bonus -= self.bonus
    
    def get_description(self) -> str:
        return f"+{self.bonus} for doubles"


@CardEffectRegistry.register("triple_bonus")
class TripleBonusEffect(CardEffect):
    """Adds bonus points for triple line clears"""
    
    def __init__(self, bonus: int):
        self.bonus = bonus
    
    def apply(self, game: 'Game') -> None:
        get_modifiers().triple_bonus += self.bonus
    
    def remove(self, game: 'Game') -> None:
        get_modifiers().triple_bonus -= self.bonus
    
    def get_description(self) -> str:
        return f"+{self.bonus} for triples"


@CardEffectRegistry.register("score_multiplier")
class ScoreMultiplierEffect(CardEffect):
    """Multiplies all scores"""
    
    def __init__(self, multiplier: float):
        self.multiplier = multiplier
    
    def apply(self, game: 'Game') -> None:
        get_modifiers().score_multiplier *= self.multiplier
    
    def remove(self, game: 'Game') -> None:
        get_modifiers().score_multiplier /= self.multiplier
    
    def get_description(self) -> str:
        return f"x{self.multiplier} all scores"


# ============ Red Card Effects - Negative ============

@CardEffectRegistry.register("frozen_line")
class FrozenLineEffect(CardEffect):
    """Freezes bottom line(s), making them unclearable"""
    
    def __init__(self, count: int):
        self.count = count
    
    def apply(self, game: 'Game') -> None:
        modifiers = get_modifiers()
        # Add frozen lines from bottom
        board_height = game.board.height
        for i in range(self.count):
            frozen_row = board_height - 1 - i
            if frozen_row not in modifiers.frozen_lines:
                modifiers.frozen_lines.append(frozen_row)
        
        # Fill the frozen lines with grey blocks
        for row in modifiers.frozen_lines:
            for x in range(game.board.width):
                if game.board.get_cell(x, row) is None:
                    game.board.set_cell(x, row, (100, 100, 100))
    
    def remove(self, game: 'Game') -> None:
        modifiers = get_modifiers()
        modifiers.frozen_lines.clear()
    
    def get_description(self) -> str:
        return f"Bottom {self.count} line(s) frozen"


@CardEffectRegistry.register("disable_hold")
class DisableHoldEffect(CardEffect):
    """Disables the hold function"""
    
    def __init__(self, disabled: bool):
        self.disabled = disabled
    
    def apply(self, game: 'Game') -> None:
        get_modifiers().hold_disabled = self.disabled
    
    def remove(self, game: 'Game') -> None:
        get_modifiers().hold_disabled = False
    
    def get_description(self) -> str:
        return "Hold disabled"


@CardEffectRegistry.register("disable_ghost")
class DisableGhostEffect(CardEffect):
    """Disables the ghost piece"""
    
    def __init__(self, disabled: bool):
        self.disabled = disabled
    
    def apply(self, game: 'Game') -> None:
        get_modifiers().ghost_disabled = self.disabled
    
    def remove(self, game: 'Game') -> None:
        get_modifiers().ghost_disabled = False
    
    def get_description(self) -> str:
        return "Ghost piece disabled"


@CardEffectRegistry.register("lock_delay_mult")
class LockDelayMultiplierEffect(CardEffect):
    """Multiplies lock delay time"""
    
    def __init__(self, multiplier: float):
        self.multiplier = multiplier
    
    def apply(self, game: 'Game') -> None:
        get_modifiers().lock_delay_multiplier *= self.multiplier
    
    def remove(self, game: 'Game') -> None:
        get_modifiers().lock_delay_multiplier /= self.multiplier
    
    def get_description(self) -> str:
        if self.multiplier < 1:
            return f"Lock delay x{self.multiplier}"
        return f"Lock delay x{self.multiplier}"


@CardEffectRegistry.register("random_hole")
class RandomHoleEffect(CardEffect):
    """Creates random holes periodically"""
    
    def __init__(self, frequency: int):
        self.frequency = frequency
    
    def apply(self, game: 'Game') -> None:
        modifiers = get_modifiers()
        if modifiers.random_hole_frequency == 0:
            modifiers.random_hole_frequency = self.frequency
        else:
            # Take the more frequent one
            modifiers.random_hole_frequency = min(
                modifiers.random_hole_frequency, 
                self.frequency
            )
    
    def remove(self, game: 'Game') -> None:
        get_modifiers().random_hole_frequency = 0
    
    def get_description(self) -> str:
        return f"Hole every {self.frequency} pieces"


@CardEffectRegistry.register("fill_column")
class FillColumnEffect(CardEffect):
    """Fills a column with blocks"""
    
    def __init__(self, column: int):
        self.column = column
    
    def apply(self, game: 'Game') -> None:
        modifiers = get_modifiers()
        if self.column not in modifiers.filled_columns:
            modifiers.filled_columns.append(self.column)
        
        # Fill the column
        for y in range(game.board.height):
            if game.board.get_cell(self.column, y) is None:
                game.board.set_cell(self.column, y, (80, 80, 80))
    
    def remove(self, game: 'Game') -> None:
        modifiers = get_modifiers()
        if self.column in modifiers.filled_columns:
            modifiers.filled_columns.remove(self.column)
    
    def get_description(self) -> str:
        return f"Column {self.column + 1} filled"


@CardEffectRegistry.register("remove_piece_type")
class RemovePieceTypeEffect(CardEffect):
    """Removes a piece type from the bag"""
    
    def __init__(self, piece_type: str):
        self.piece_type = piece_type
        self.removed_type = None
    
    def apply(self, game: 'Game') -> None:
        import random
        modifiers = get_modifiers()
        
        if self.piece_type == "random":
            # Pick a random piece type that hasn't been removed yet
            from config import game_config
            available = [p for p in game_config.get_all_piece_types() 
                        if p not in modifiers.removed_piece_types]
            if available:
                self.removed_type = random.choice(available)
                modifiers.removed_piece_types.append(self.removed_type)
        else:
            if self.piece_type not in modifiers.removed_piece_types:
                modifiers.removed_piece_types.append(self.piece_type)
                self.removed_type = self.piece_type
        
        # Update piece generator
        if self.removed_type and hasattr(game.piece_generator, 'remove_piece_type'):
            game.piece_generator.remove_piece_type(self.removed_type)
    
    def remove(self, game: 'Game') -> None:
        if self.removed_type:
            modifiers = get_modifiers()
            if self.removed_type in modifiers.removed_piece_types:
                modifiers.removed_piece_types.remove(self.removed_type)
    
    def get_description(self) -> str:
        if self.removed_type:
            return f"No more {self.removed_type} pieces"
        return "One piece type removed"


# ============ Orange Card Effects - Rare Bonuses ============

@CardEffectRegistry.register("clear_board")
class ClearBoardEffect(CardEffect):
    """Clears the entire board"""
    
    def __init__(self, clear: bool):
        self.clear = clear
    
    def apply(self, game: 'Game') -> None:
        if self.clear:
            game.board.clear()
    
    def remove(self, game: 'Game') -> None:
        pass  # One-time effect
    
    def get_description(self) -> str:
        return "Board cleared!"


# ============ Grey Card Effects - Meta ============

@CardEffectRegistry.register("remove_card")
class RemoveCardEffect(CardEffect):
    """Triggers card removal selection"""
    
    def __init__(self, count: int):
        self.count = count
    
    def apply(self, game: 'Game') -> None:
        # Set flag to trigger card removal selection phase
        if hasattr(game, 'pending_card_removal'):
            game.pending_card_removal = self.count
    
    def remove(self, game: 'Game') -> None:
        pass
    
    def get_description(self) -> str:
        return f"Remove {self.count} card(s)"


@CardEffectRegistry.register("upgrade_card")
class UpgradeCardEffect(CardEffect):
    """Doubles a random green card's numeric effect"""
    
    def __init__(self, card_type: str):
        self.card_type = card_type
        self.upgraded_card_id = None
    
    def apply(self, game: 'Game') -> None:
        import random
        from core.cards import CardType
        
        modifiers = get_modifiers()
        
        # Find cards of the target type
        target_cards = [c for c in game.card_manager.collected_cards_list 
                       if c.type.value == self.card_type]
        
        if target_cards:
            # Pick a random one to upgrade
            card_to_upgrade = random.choice(target_cards)
            self.upgraded_card_id = card_to_upgrade.id
            
            # Double the effect based on effect_id
            if card_to_upgrade.effect_id == "tetris_bonus":
                modifiers.tetris_bonus += card_to_upgrade.effect_value
            elif card_to_upgrade.effect_id == "b2b_bonus":
                modifiers.b2b_bonus += card_to_upgrade.effect_value
            elif card_to_upgrade.effect_id == "line_bonus":
                modifiers.line_bonus += card_to_upgrade.effect_value
            elif card_to_upgrade.effect_id == "hard_drop_bonus":
                modifiers.hard_drop_bonus += card_to_upgrade.effect_value
            elif card_to_upgrade.effect_id == "double_bonus":
                modifiers.double_bonus += card_to_upgrade.effect_value
            elif card_to_upgrade.effect_id == "triple_bonus":
                modifiers.triple_bonus += card_to_upgrade.effect_value
            elif card_to_upgrade.effect_id == "combo_bonus":
                # Add another combo bonus entry
                value = card_to_upgrade.effect_value
                if isinstance(value, dict):
                    modifiers.combo_bonuses.append({
                        "min_combo": value.get("min_combo", 2),
                        "multiplier_bonus": value.get("multiplier_bonus", 1.0)
                    })
    
    def remove(self, game: 'Game') -> None:
        pass
    
    def get_description(self) -> str:
        return f"Upgrade a {self.card_type} card"


@CardEffectRegistry.register("remove_type")
class RemoveTypeEffect(CardEffect):
    """Removes all cards of a specific type and reverses their effects"""
    
    def __init__(self, card_type: str):
        self.card_type = card_type
        self.removed_cards = []
    
    def apply(self, game: 'Game') -> None:
        from core.cards import CardType
        
        # Find all cards of this type
        cards_to_remove = [c for c in game.card_manager.collected_cards_list[:]
                          if c.type.value == self.card_type]
        
        for card in cards_to_remove:
            self.removed_cards.append(card)
            
            # Reverse the card's effect
            self._reverse_card_effect(card, game)
            
            # Remove from the card manager's list
            game.card_manager.remove_card_from_list(card)
    
    def _reverse_card_effect(self, card, game: 'Game') -> None:
        """Reverse a card's effect"""
        modifiers = get_modifiers()
        
        if card.effect_id == "frozen_line":
            # Unfreeze lines
            modifiers.frozen_lines.clear()
        elif card.effect_id == "disable_hold":
            modifiers.hold_disabled = False
        elif card.effect_id == "disable_ghost":
            modifiers.ghost_disabled = False
        elif card.effect_id == "lock_delay_mult":
            # Reverse multiplier
            if card.effect_value and card.effect_value != 0:
                modifiers.lock_delay_multiplier /= card.effect_value
        elif card.effect_id == "random_hole":
            modifiers.random_hole_frequency = 0
        elif card.effect_id == "fill_column":
            # Clear the filled column
            if card.effect_value in modifiers.filled_columns:
                modifiers.filled_columns.remove(card.effect_value)
            for y in range(game.board.height):
                if game.board.get_cell(card.effect_value, y) == (80, 80, 80):
                    game.board.set_cell(card.effect_value, y, None)
        elif card.effect_id == "remove_piece_type":
            # Re-add the removed piece type
            if card.effect_value in modifiers.removed_piece_types:
                modifiers.removed_piece_types.remove(card.effect_value)
    
    def remove(self, game: 'Game') -> None:
        pass
    
    def get_description(self) -> str:
        return f"Remove all {self.card_type} cards"


@CardEffectRegistry.register("reroll_choices")
class RerollChoicesEffect(CardEffect):
    """Triggers reroll of all card choices"""
    
    def __init__(self, reroll: bool):
        self.reroll = reroll
    
    def apply(self, game: 'Game') -> None:
        # Set flag to trigger reroll
        if hasattr(game, 'pending_reroll'):
            game.pending_reroll = True
    
    def remove(self, game: 'Game') -> None:
        pass
    
    def get_description(self) -> str:
        return "Reroll all choices"


@CardEffectRegistry.register("duplicate_last")
class DuplicateLastEffect(CardEffect):
    """Duplicates the last picked card's effect"""
    
    def __init__(self, duplicate: bool):
        self.duplicate = duplicate
        self.duplicated_card = None
    
    def apply(self, game: 'Game') -> None:
        # Get the last collected card (excluding this grey card)
        if len(game.card_manager.collected_cards_list) > 0:
            # Find the last non-grey card
            for card in reversed(game.card_manager.collected_cards_list):
                if card.type.value != "grey":
                    self.duplicated_card = card
                    break
            
            if self.duplicated_card:
                # Apply that card's effect again
                apply_card_effect(game, self.duplicated_card)
                
                # Add it to the collected list again (for display)
                game.card_manager.collected_cards_list.append(self.duplicated_card)
                
                # Update stack count
                if self.duplicated_card.id in game.card_manager.collected_cards:
                    game.card_manager.collected_cards[self.duplicated_card.id].stack_count += 1
    
    def remove(self, game: 'Game') -> None:
        pass
    
    def get_description(self) -> str:
        return "Copy last card"


def apply_card_effect(game: 'Game', card: CardData) -> None:
    """Apply a card's effect to the game"""
    if not card.effect_id:
        # Blue cards add pieces directly
        if card.type == CardType.BLUE and card.piece_shape:
            effect = AddPieceEffect(card.id, card.piece_shape, card.piece_color or "#FFFFFF")
            effect.apply(game)
        return
    
    # Create and apply the effect
    effect_value = card.effect_value
    
    if card.effect_id == "combo_bonus" and isinstance(effect_value, dict):
        effect = ComboBonusEffect(
            effect_value.get("min_combo", 2),
            effect_value.get("multiplier_bonus", 1.0)
        )
    elif card.effect_id == "tetris_bonus":
        effect = TetrisBonusEffect(effect_value)
    elif card.effect_id == "b2b_bonus":
        effect = B2BBonusEffect(effect_value)
    elif card.effect_id == "line_bonus":
        effect = LineBonusEffect(effect_value)
    elif card.effect_id == "hard_drop_bonus":
        effect = HardDropBonusEffect(effect_value)
    elif card.effect_id == "double_bonus":
        effect = DoubleBonusEffect(effect_value)
    elif card.effect_id == "triple_bonus":
        effect = TripleBonusEffect(effect_value)
    elif card.effect_id == "score_multiplier":
        effect = ScoreMultiplierEffect(effect_value)
    elif card.effect_id == "frozen_line":
        effect = FrozenLineEffect(effect_value)
    elif card.effect_id == "disable_hold":
        effect = DisableHoldEffect(effect_value)
    elif card.effect_id == "disable_ghost":
        effect = DisableGhostEffect(effect_value)
    elif card.effect_id == "lock_delay_mult":
        effect = LockDelayMultiplierEffect(effect_value)
    elif card.effect_id == "random_hole":
        effect = RandomHoleEffect(effect_value)
    elif card.effect_id == "fill_column":
        effect = FillColumnEffect(effect_value)
    elif card.effect_id == "remove_piece_type":
        effect = RemovePieceTypeEffect(effect_value)
    elif card.effect_id == "clear_board":
        effect = ClearBoardEffect(effect_value)
    else:
        return
    
    effect.apply(game)
    
    # Track the card
    modifiers = get_modifiers()
    modifiers.cards_collected.append(card.id)
    modifiers.last_card_id = card.id

