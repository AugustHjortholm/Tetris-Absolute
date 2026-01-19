"""
Tests for the roguelike card system.
Tests card types, effects, stacking, and selection.
"""

import pytest
from core.cards import CardType, CardData, CardManager, CollectedCard
from config import cards_config


class TestCardTypes:
    """Tests for card type enum"""
    
    def test_card_types_exist(self):
        """Test all card types exist"""
        assert CardType.BLUE.value == "blue"
        assert CardType.GREEN.value == "green"
        assert CardType.RED.value == "red"
        assert CardType.ORANGE.value == "orange"
        assert CardType.GREY.value == "grey"
    
    def test_all_card_types(self):
        """Test we have exactly 5 card types"""
        assert len(CardType) == 5


class TestCardData:
    """Tests for CardData structure"""
    
    def test_create_card_data(self):
        """Test creating a card data instance"""
        card = CardData(
            id="test_card",
            type=CardType.BLUE,
            name="Test Card",
            description="A test card",
            speed_change=1
        )
        assert card.id == "test_card"
        assert card.type == CardType.BLUE
        assert card.name == "Test Card"
        assert card.speed_change == 1
    
    def test_stackable_card(self):
        """Test stackable card properties"""
        card = CardData(
            id="stack_card",
            type=CardType.GREEN,
            name="Stackable",
            description="Can stack",
            speed_change=2,
            stackable=True,
            max_stack=3
        )
        assert card.stackable == True
        assert card.max_stack == 3
    
    def test_card_with_piece_shape(self):
        """Test blue card with piece shape"""
        shape = [[1, 1, 1, 1, 1]]
        card = CardData(
            id="long_piece",
            type=CardType.BLUE,
            name="Long Piece",
            description="5-block piece",
            speed_change=1,
            piece_shape=shape,
            piece_color="#00CED1"
        )
        assert card.piece_shape == shape
        assert card.piece_color == "#00CED1"


class TestCardsConfig:
    """Tests for cards configuration loading"""
    
    def test_cards_config_exists(self):
        """Test cards config loads correctly"""
        assert cards_config is not None
    
    def test_cards_per_selection(self):
        """Test cards per selection setting"""
        assert cards_config.cards_per_selection == 3
    
    def test_lines_between_selections(self):
        """Test lines between selections setting"""
        assert cards_config.lines_between_selections == 10
    
    def test_blue_cards_exist(self):
        """Test blue cards are defined"""
        assert len(cards_config.blue_cards) > 0
    
    def test_green_cards_exist(self):
        """Test green cards are defined"""
        assert len(cards_config.green_cards) > 0
    
    def test_red_cards_exist(self):
        """Test red cards are defined"""
        assert len(cards_config.red_cards) > 0
    
    def test_orange_cards_exist(self):
        """Test orange cards are defined"""
        assert len(cards_config.orange_cards) > 0
    
    def test_grey_cards_exist(self):
        """Test grey cards are defined"""
        assert len(cards_config.grey_cards) > 0
    
    def test_card_colors_defined(self):
        """Test card colors are defined for all types"""
        for card_type in ["blue", "green", "red", "orange", "grey"]:
            bg = cards_config.get_card_color(card_type, "background")
            assert isinstance(bg, tuple)
            assert len(bg) == 3


class TestCardManager:
    """Tests for CardManager"""
    
    @pytest.fixture
    def manager(self):
        """Create a card manager for testing"""
        return CardManager(cards_config.all_cards)
    
    def test_manager_initialization(self, manager):
        """Test card manager initializes correctly"""
        assert manager is not None
        assert len(manager.all_cards) > 0
    
    def test_initial_speed_level(self, manager):
        """Test initial speed level is 1"""
        assert manager.current_speed_level == 1
    
    def test_select_cards(self, manager):
        """Test selecting cards returns correct count"""
        cards = manager.select_cards(3)
        assert len(cards) <= 3
        assert all(isinstance(c, CardData) for c in cards)
    
    def test_grey_cards_not_first(self, manager):
        """Test grey cards are not available in first selection"""
        # First selection
        cards = manager.select_cards(100)  # Get all possible cards
        grey_cards = [c for c in cards if c.type == CardType.GREY]
        assert len(grey_cards) == 0
    
    def test_collect_card_updates_speed(self, manager):
        """Test collecting a card updates speed level"""
        initial_speed = manager.current_speed_level
        
        # Create a card with speed change
        card = CardData(
            id="test",
            type=CardType.GREEN,
            name="Test",
            description="Test",
            speed_change=2
        )
        manager.all_cards["test"] = card
        manager.collect_card(card)
        
        assert manager.current_speed_level == initial_speed + 2
    
    def test_negative_speed_change(self, manager):
        """Test red card decreases speed"""
        initial_speed = manager.current_speed_level
        
        card = CardData(
            id="red_test",
            type=CardType.RED,
            name="Red Test",
            description="Test",
            speed_change=-1
        )
        manager.all_cards["red_test"] = card
        manager.collect_card(card)
        
        # Speed should not go below 1
        expected = max(1, initial_speed - 1)
        assert manager.current_speed_level == expected
    
    def test_stackable_card_collection(self, manager):
        """Test collecting stackable cards"""
        card = CardData(
            id="stack_test",
            type=CardType.GREEN,
            name="Stack Test",
            description="Test",
            speed_change=1,
            stackable=True,
            max_stack=3
        )
        manager.all_cards["stack_test"] = card
        
        # Collect the same card twice
        manager.collect_card(card)
        manager.collect_card(card)
        
        assert manager.get_collected_count("stack_test") == 2
    
    def test_max_stack_limits_availability(self, manager):
        """Test that maxed stack cards are not available"""
        card = CardData(
            id="max_stack_test",
            type=CardType.GREEN,
            name="Max Test",
            description="Test",
            speed_change=1,
            stackable=True,
            max_stack=2
        )
        manager.all_cards["max_stack_test"] = card
        
        # Collect to max
        manager.collect_card(card)
        manager.collect_card(card)
        
        assert not manager.is_card_available(card)
    
    def test_reset(self, manager):
        """Test manager reset clears state"""
        card = CardData(
            id="reset_test",
            type=CardType.GREEN,
            name="Reset Test",
            description="Test",
            speed_change=5
        )
        manager.all_cards["reset_test"] = card
        manager.collect_card(card)
        
        manager.reset()
        
        assert manager.current_speed_level == 1
        assert manager.get_collected_count("reset_test") == 0
        assert manager.card_selection_count == 0


class TestCollectedCard:
    """Tests for CollectedCard structure"""
    
    def test_collected_card_creation(self):
        """Test creating a collected card"""
        card_data = CardData(
            id="test",
            type=CardType.BLUE,
            name="Test",
            description="Test",
            speed_change=1
        )
        collected = CollectedCard(card_data=card_data)
        
        assert collected.card_data == card_data
        assert collected.stack_count == 1
    
    def test_collected_card_stack_count(self):
        """Test collected card with stack count"""
        card_data = CardData(
            id="test",
            type=CardType.GREEN,
            name="Test",
            description="Test",
            speed_change=1,
            stackable=True,
            max_stack=5
        )
        collected = CollectedCard(card_data=card_data, stack_count=3)
        
        assert collected.stack_count == 3


class TestCardDefaultSpeeds:
    """Tests for default speed values by card type"""
    
    def test_blue_default_speed(self):
        """Test blue cards default to +1 speed"""
        for card in cards_config.blue_cards:
            assert card.get("speed_change", 1) >= 0  # Blue should be positive
    
    def test_green_default_speed(self):
        """Test green cards default to +2 speed"""
        for card in cards_config.green_cards:
            assert card.get("speed_change", 2) > 0  # Green should be positive
    
    def test_red_default_speed(self):
        """Test red cards default to -1 speed"""
        for card in cards_config.red_cards:
            assert card.get("speed_change", -1) < 0  # Red should be negative
    
    def test_grey_default_speed(self):
        """Test grey cards default to +1 speed"""
        for card in cards_config.grey_cards:
            assert card.get("speed_change", 1) >= 0  # Grey should be positive


class TestBlueCardPieces:
    """Tests for blue card piece definitions"""
    
    def test_blue_cards_have_shapes(self):
        """Test all blue cards have piece shapes"""
        for card in cards_config.blue_cards:
            assert "piece_shape" in card
            assert isinstance(card["piece_shape"], list)
            assert len(card["piece_shape"]) > 0
    
    def test_blue_cards_have_colors(self):
        """Test all blue cards have piece colors"""
        for card in cards_config.blue_cards:
            assert "piece_color" in card
            assert card["piece_color"].startswith("#")


class TestGreenCardEffects:
    """Tests for green card effect definitions"""
    
    def test_green_cards_have_effects(self):
        """Test green cards have effect IDs"""
        for card in cards_config.green_cards:
            assert "effect_id" in card
    
    def test_green_cards_stackable(self):
        """Test green cards are properly marked as stackable"""
        for card in cards_config.green_cards:
            if card.get("stackable", False):
                assert "max_stack" in card
                assert card["max_stack"] > 1


class TestRedCardEffects:
    """Tests for red card effect definitions"""
    
    def test_red_cards_have_effects(self):
        """Test red cards have effect IDs"""
        for card in cards_config.red_cards:
            assert "effect_id" in card
    
    def test_red_cards_negative_speed(self):
        """Test red cards have negative or zero speed change"""
        for card in cards_config.red_cards:
            speed = card.get("speed_change", -1)
            assert speed <= 0


class TestCardRarity:
    """Tests for card rarity system"""
    
    def test_orange_cards_have_low_rarity(self):
        """Test orange cards have lower rarity values"""
        for card in cards_config.orange_cards:
            rarity = card.get("rarity", 1.0)
            # Orange should be rarer (lower value)
            assert rarity <= 0.5
    
    def test_standard_cards_default_rarity(self):
        """Test standard cards have higher rarity values"""
        for card in cards_config.blue_cards:
            rarity = card.get("rarity", 1.0)
            assert rarity >= 0.5


class TestGreyCardValidation:
    """Tests for grey card target validation"""
    
    @pytest.fixture
    def manager(self):
        return CardManager(cards_config.all_cards)
    
    def test_grey_cards_need_targets(self, manager):
        """Test grey cards are not available without valid targets"""
        # With no collected cards, grey cards should not be available
        grey_cards = manager.get_available_cards_by_type(CardType.GREY)
        
        # Only reroll_choices should be available (doesn't need targets)
        for card in grey_cards:
            assert card.effect_id == "reroll_choices"
    
    def test_grey_remove_card_needs_cards(self, manager):
        """Test remove_card grey card needs collected cards"""
        remove_card = None
        for card in manager.all_cards.values():
            if card.type == CardType.GREY and card.effect_id == "remove_card":
                remove_card = card
                break
        
        if remove_card:
            # Should not be available initially
            assert not manager._grey_card_has_valid_target(remove_card)
            
            # Collect a card
            test_card = CardData(
                id="test", type=CardType.BLUE, name="Test",
                description="Test", speed_change=1
            )
            manager.all_cards["test"] = test_card
            manager.collect_card(test_card)
            
            # Now should be available
            assert manager._grey_card_has_valid_target(remove_card)
    
    def test_grey_upgrade_needs_matching_type(self, manager):
        """Test upgrade grey card needs cards of target type"""
        upgrade_card = None
        for card in manager.all_cards.values():
            if card.type == CardType.GREY and card.effect_id == "upgrade_card":
                upgrade_card = card
                break
        
        if upgrade_card:
            # Collect a blue card
            blue_card = CardData(
                id="test_blue", type=CardType.BLUE, name="Test Blue",
                description="Test", speed_change=1
            )
            manager.all_cards["test_blue"] = blue_card
            manager.collect_card(blue_card)
            
            # upgrade_card targets green cards, so should not be available
            assert not manager._grey_card_has_valid_target(upgrade_card)
            
            # Collect a green card
            green_card = CardData(
                id="test_green", type=CardType.GREEN, name="Test Green",
                description="Test", speed_change=2
            )
            manager.all_cards["test_green"] = green_card
            manager.collect_card(green_card)
            
            # Now should be available
            assert manager._grey_card_has_valid_target(upgrade_card)


class TestCollectedCardsList:
    """Tests for collected cards list ordering"""
    
    @pytest.fixture
    def manager(self):
        return CardManager(cards_config.all_cards)
    
    def test_collected_cards_list_empty_initially(self, manager):
        """Test collected cards list is empty initially"""
        assert len(manager.collected_cards_list) == 0
    
    def test_collected_cards_list_ordered(self, manager):
        """Test collected cards list maintains order"""
        card1 = CardData(
            id="first", type=CardType.BLUE, name="First",
            description="Test", speed_change=1
        )
        card2 = CardData(
            id="second", type=CardType.GREEN, name="Second",
            description="Test", speed_change=2
        )
        manager.all_cards["first"] = card1
        manager.all_cards["second"] = card2
        
        manager.collect_card(card1)
        manager.collect_card(card2)
        
        assert len(manager.collected_cards_list) == 2
        assert manager.collected_cards_list[0] == card1
        assert manager.collected_cards_list[1] == card2
    
    def test_remove_card_from_list(self, manager):
        """Test removing a card from the list"""
        card1 = CardData(
            id="to_keep", type=CardType.BLUE, name="Keep",
            description="Test", speed_change=1
        )
        card2 = CardData(
            id="to_remove", type=CardType.GREEN, name="Remove",
            description="Test", speed_change=2
        )
        manager.all_cards["to_keep"] = card1
        manager.all_cards["to_remove"] = card2
        
        manager.collect_card(card1)
        manager.collect_card(card2)
        
        # Remove the second card
        manager.remove_card_from_list(card2)
        
        assert len(manager.collected_cards_list) == 1
        assert manager.collected_cards_list[0] == card1
    
    def test_remove_card_reverses_speed(self, manager):
        """Test removing a card reverses speed change"""
        card = CardData(
            id="speed_card", type=CardType.GREEN, name="Speed",
            description="Test", speed_change=3
        )
        manager.all_cards["speed_card"] = card
        
        initial_speed = manager.current_speed_level
        manager.collect_card(card)
        assert manager.current_speed_level == initial_speed + 3
        
        manager.remove_card_from_list(card)
        assert manager.current_speed_level == initial_speed
    
    def test_reset_clears_list(self, manager):
        """Test reset clears collected cards list"""
        card = CardData(
            id="test", type=CardType.BLUE, name="Test",
            description="Test", speed_change=1
        )
        manager.all_cards["test"] = card
        manager.collect_card(card)
        
        manager.reset()
        
        assert len(manager.collected_cards_list) == 0

