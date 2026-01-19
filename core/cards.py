"""
Card system for roguelike elements.
Defines card types, effects, and management.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Any, Optional, Callable, TYPE_CHECKING
import random

if TYPE_CHECKING:
    from game import Game


class CardType(Enum):
    """Card color/type categories"""
    BLUE = "blue"      # New tetris pieces
    GREEN = "green"    # Point bonuses
    RED = "red"        # Negative effects
    ORANGE = "orange"  # Rare bonuses
    GREY = "grey"      # Meta effects


@dataclass
class CardData:
    """Data structure for card definitions loaded from JSON"""
    id: str
    type: CardType
    name: str
    description: str
    speed_change: int
    stackable: bool = False
    max_stack: int = 1
    rarity: float = 1.0  # Rarity weight (lower = rarer)
    
    # Type-specific data
    piece_shape: Optional[List[List[int]]] = None  # For blue cards
    piece_color: Optional[str] = None              # Hex color for new piece
    effect_id: Optional[str] = None                # For effects
    effect_value: Optional[Any] = None             # Effect parameter
    
    # For grey cards
    requires_previous_cards: bool = False          # True for grey cards


@dataclass
class CollectedCard:
    """A card the player has collected with its stack count"""
    card_data: CardData
    stack_count: int = 1


class CardEffect(ABC):
    """Abstract base class for card effects"""
    
    @abstractmethod
    def apply(self, game: 'Game') -> None:
        """Apply the effect to the game"""
        pass
    
    @abstractmethod
    def remove(self, game: 'Game') -> None:
        """Remove the effect from the game (if applicable)"""
        pass
    
    @abstractmethod
    def get_description(self) -> str:
        """Get the effect description"""
        pass


class CardManager:
    """Manages card pools, selection, and collected cards"""
    
    def __init__(self, cards_config: Dict[str, Any]):
        self.cards_config = cards_config
        self.all_cards: Dict[str, CardData] = {}
        self.collected_cards: Dict[str, CollectedCard] = {}
        self.collected_cards_list: List[CardData] = []  # Ordered list for display
        self.card_selection_count = 0  # Track how many times cards have been selected
        self.current_speed_level = 1
        
        self._load_cards()
    
    def _load_cards(self) -> None:
        """Load all card definitions from config"""
        for card_type in CardType:
            type_key = card_type.value + "_cards"
            if type_key in self.cards_config:
                for card_config in self.cards_config[type_key]:
                    card_data = CardData(
                        id=card_config["id"],
                        type=card_type,
                        name=card_config["name"],
                        description=card_config["description"],
                        speed_change=card_config.get("speed_change", self._get_default_speed(card_type)),
                        stackable=card_config.get("stackable", False),
                        max_stack=card_config.get("max_stack", 1),
                        rarity=card_config.get("rarity", 1.0),
                        piece_shape=card_config.get("piece_shape"),
                        piece_color=card_config.get("piece_color"),
                        effect_id=card_config.get("effect_id"),
                        effect_value=card_config.get("effect_value"),
                        requires_previous_cards=card_type == CardType.GREY
                    )
                    self.all_cards[card_data.id] = card_data
    
    def _get_default_speed(self, card_type: CardType) -> int:
        """Get default speed change for a card type"""
        defaults = {
            CardType.BLUE: 1,
            CardType.GREEN: 2,
            CardType.RED: -1,
            CardType.ORANGE: 2,
            CardType.GREY: 1
        }
        return defaults.get(card_type, 0)
    
    def is_card_available(self, card: CardData) -> bool:
        """Check if a card can be selected"""
        # Grey cards require having cards they can affect
        if card.type == CardType.GREY:
            if not self._grey_card_has_valid_target(card):
                return False
        
        # Check stack limits
        if card.id in self.collected_cards:
            collected = self.collected_cards[card.id]
            if not card.stackable or collected.stack_count >= card.max_stack:
                return False
        
        return True
    
    def _grey_card_has_valid_target(self, card: CardData) -> bool:
        """Check if a grey card has valid targets to affect"""
        # No collected cards = no valid target for most grey cards
        if not self.collected_cards_list:
            return False
        
        effect_id = card.effect_id
        
        if effect_id == "remove_card":
            # Can remove any collected card
            return len(self.collected_cards_list) > 0
        
        elif effect_id == "upgrade_card":
            # Can only upgrade green cards
            target_type = card.effect_value  # "green"
            return any(c.type.value == target_type for c in self.collected_cards_list)
        
        elif effect_id == "remove_type":
            # Can only remove if we have cards of that type
            target_type = card.effect_value  # "red"
            return any(c.type.value == target_type for c in self.collected_cards_list)
        
        elif effect_id == "duplicate_last":
            # Can only duplicate if we have a last card
            return len(self.collected_cards_list) > 0
        
        elif effect_id == "reroll_choices":
            # This one doesn't need previous cards, always available
            return True
        
        # Default: require at least one collected card
        return len(self.collected_cards_list) > 0
    
    def get_available_cards_by_type(self, card_type: CardType) -> List[CardData]:
        """Get all available cards of a specific type"""
        available = []
        for card in self.all_cards.values():
            if card.type == card_type and self.is_card_available(card):
                available.append(card)
        return available
    
    def select_cards(self, count: int = 3) -> List[CardData]:
        """Select cards for the player to choose from"""
        selected: List[CardData] = []
        
        # Build weighted pool
        available_cards: List[CardData] = []
        weights: List[float] = []
        
        for card in self.all_cards.values():
            if self.is_card_available(card):
                # Apply rarity weights
                weight = card.rarity
                
                # Orange cards are much rarer
                if card.type == CardType.ORANGE:
                    weight *= 0.1
                
                available_cards.append(card)
                weights.append(weight)
        
        if not available_cards:
            return []
        
        # Select unique cards
        remaining_cards = list(zip(available_cards, weights))
        
        for _ in range(min(count, len(remaining_cards))):
            if not remaining_cards:
                break
            
            cards, card_weights = zip(*remaining_cards)
            total_weight = sum(card_weights)
            normalized_weights = [w / total_weight for w in card_weights]
            
            chosen_idx = random.choices(range(len(cards)), weights=normalized_weights, k=1)[0]
            chosen_card = cards[chosen_idx]
            
            # Grey cards that can't affect anything get rerolled
            if chosen_card.type == CardType.GREY and not self._grey_card_has_valid_target(chosen_card):
                # Reroll to a non-grey card
                rerolled = self._reroll_grey_card(remaining_cards, chosen_idx)
                if rerolled:
                    chosen_card = rerolled
                else:
                    # No valid reroll, skip this card
                    remaining_cards.pop(chosen_idx)
                    continue
            
            selected.append(chosen_card)
            
            # Remove chosen card from pool
            remaining_cards.pop(chosen_idx)
        
        return selected
    
    def _reroll_grey_card(self, remaining_cards: List, exclude_idx: int) -> Optional[CardData]:
        """Reroll a grey card to a non-grey card"""
        non_grey = [(c, w) for i, (c, w) in enumerate(remaining_cards) 
                    if i != exclude_idx and c.type != CardType.GREY]
        
        if not non_grey:
            return None
        
        cards, weights = zip(*non_grey)
        total = sum(weights)
        normalized = [w / total for w in weights]
        
        chosen_idx = random.choices(range(len(cards)), weights=normalized, k=1)[0]
        return cards[chosen_idx]
    
    def collect_card(self, card: CardData) -> None:
        """Add a card to the player's collection"""
        if card.id in self.collected_cards:
            self.collected_cards[card.id].stack_count += 1
        else:
            self.collected_cards[card.id] = CollectedCard(card_data=card)
        
        # Add to ordered list for display
        self.collected_cards_list.append(card)
        
        # Update speed level
        self.current_speed_level += card.speed_change
        if self.current_speed_level < 1:
            self.current_speed_level = 1
        
        self.card_selection_count += 1
    
    def remove_card_from_list(self, card: CardData) -> None:
        """Remove a card from the collected list (for grey card effects)"""
        if card in self.collected_cards_list:
            self.collected_cards_list.remove(card)
            
            # Update the collected_cards dict
            if card.id in self.collected_cards:
                self.collected_cards[card.id].stack_count -= 1
                if self.collected_cards[card.id].stack_count <= 0:
                    del self.collected_cards[card.id]
            
            # Reverse the speed change
            self.current_speed_level -= card.speed_change
            if self.current_speed_level < 1:
                self.current_speed_level = 1
    
    def get_collected_count(self, card_id: str) -> int:
        """Get how many times a card has been collected"""
        if card_id in self.collected_cards:
            return self.collected_cards[card_id].stack_count
        return 0
    
    def get_all_collected(self) -> List[CollectedCard]:
        """Get all collected cards"""
        return list(self.collected_cards.values())
    
    def reroll_card(self, original_card: CardData, fallback_type: CardType = CardType.RED) -> Optional[CardData]:
        """Reroll a card to a different one of the same type, or fallback type"""
        same_type = self.get_available_cards_by_type(original_card.type)
        same_type = [c for c in same_type if c.id != original_card.id]
        
        if same_type:
            return random.choice(same_type)
        
        # Fallback to different type
        fallback_cards = self.get_available_cards_by_type(fallback_type)
        if fallback_cards:
            return random.choice(fallback_cards)
        
        return None
    
    def reset(self) -> None:
        """Reset the card manager"""
        self.collected_cards.clear()
        self.collected_cards_list.clear()
        self.card_selection_count = 0
        self.current_speed_level = 1


class CardEffectRegistry:
    """Registry for card effect implementations"""
    
    _effects: Dict[str, type] = {}
    
    @classmethod
    def register(cls, effect_id: str) -> Callable:
        """Decorator to register an effect"""
        def decorator(effect_class: type) -> type:
            cls._effects[effect_id] = effect_class
            return effect_class
        return decorator
    
    @classmethod
    def create(cls, effect_id: str, **kwargs) -> Optional[CardEffect]:
        """Create an effect instance"""
        if effect_id in cls._effects:
            return cls._effects[effect_id](**kwargs)
        return None

