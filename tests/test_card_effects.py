"""
Tests for card effect implementations.
Tests game modifiers and effect application.
"""

import pytest
from implementations.card_effects import (
    GameModifiers, get_modifiers, set_modifiers,
    ComboBonusEffect, TetrisBonusEffect, B2BBonusEffect,
    LineBonusEffect, HardDropBonusEffect, DoubleBonusEffect,
    TripleBonusEffect, ScoreMultiplierEffect, DisableHoldEffect,
    DisableGhostEffect, LockDelayMultiplierEffect
)


class TestGameModifiers:
    """Tests for GameModifiers class"""
    
    @pytest.fixture
    def modifiers(self):
        """Create fresh modifiers for each test"""
        mod = GameModifiers()
        set_modifiers(mod)
        return mod
    
    def test_initial_state(self, modifiers):
        """Test initial modifier state"""
        assert modifiers.tetris_bonus == 0.0
        assert modifiers.b2b_bonus == 0.0
        assert modifiers.line_bonus == 0
        assert modifiers.hard_drop_bonus == 0
        assert modifiers.score_multiplier == 1.0
        assert modifiers.hold_disabled == False
        assert modifiers.ghost_disabled == False
        assert modifiers.lock_delay_multiplier == 1.0
    
    def test_reset(self, modifiers):
        """Test resetting modifiers"""
        modifiers.tetris_bonus = 5.0
        modifiers.hold_disabled = True
        modifiers.reset()
        
        assert modifiers.tetris_bonus == 0.0
        assert modifiers.hold_disabled == False
    
    def test_combo_bonus_calculation(self, modifiers):
        """Test combo bonus multiplier calculation"""
        modifiers.combo_bonuses.append({
            "min_combo": 3,
            "multiplier_bonus": 2.0
        })
        modifiers.combo_bonuses.append({
            "min_combo": 5,
            "multiplier_bonus": 3.0
        })
        
        # Combo 2 - no bonus
        assert modifiers.get_total_combo_bonus(2) == 0.0
        
        # Combo 3 - first bonus applies
        assert modifiers.get_total_combo_bonus(3) == 2.0
        
        # Combo 5 - both bonuses apply
        assert modifiers.get_total_combo_bonus(5) == 5.0
    
    def test_frozen_lines_tracking(self, modifiers):
        """Test frozen lines list"""
        modifiers.frozen_lines.append(19)
        modifiers.frozen_lines.append(18)
        
        assert 19 in modifiers.frozen_lines
        assert 18 in modifiers.frozen_lines
        assert len(modifiers.frozen_lines) == 2
    
    def test_extra_pieces_tracking(self, modifiers):
        """Test extra pieces list"""
        modifiers.extra_pieces.append({
            "id": "test_piece",
            "shape": [[1, 1, 1]],
            "color": "#FF0000"
        })
        
        assert len(modifiers.extra_pieces) == 1
        assert modifiers.extra_pieces[0]["id"] == "test_piece"


class TestScoringEffects:
    """Tests for scoring-related effects"""
    
    @pytest.fixture
    def modifiers(self):
        mod = GameModifiers()
        set_modifiers(mod)
        return mod
    
    def test_tetris_bonus_effect(self, modifiers):
        """Test Tetris bonus effect"""
        effect = TetrisBonusEffect(0.5)
        effect.apply(None)
        
        assert modifiers.tetris_bonus == 0.5
        
        effect.remove(None)
        assert modifiers.tetris_bonus == 0.0
    
    def test_b2b_bonus_effect(self, modifiers):
        """Test Back-to-Back bonus effect"""
        effect = B2BBonusEffect(1.0)
        effect.apply(None)
        
        assert modifiers.b2b_bonus == 1.0
        
        effect.remove(None)
        assert modifiers.b2b_bonus == 0.0
    
    def test_line_bonus_effect(self, modifiers):
        """Test line bonus effect"""
        effect = LineBonusEffect(50)
        effect.apply(None)
        
        assert modifiers.line_bonus == 50
        
        effect.remove(None)
        assert modifiers.line_bonus == 0
    
    def test_hard_drop_bonus_effect(self, modifiers):
        """Test hard drop bonus effect"""
        effect = HardDropBonusEffect(3)
        effect.apply(None)
        
        assert modifiers.hard_drop_bonus == 3
        
        effect.remove(None)
        assert modifiers.hard_drop_bonus == 0
    
    def test_double_bonus_effect(self, modifiers):
        """Test double line clear bonus effect"""
        effect = DoubleBonusEffect(200)
        effect.apply(None)
        
        assert modifiers.double_bonus == 200
        
        effect.remove(None)
        assert modifiers.double_bonus == 0
    
    def test_triple_bonus_effect(self, modifiers):
        """Test triple line clear bonus effect"""
        effect = TripleBonusEffect(400)
        effect.apply(None)
        
        assert modifiers.triple_bonus == 400
        
        effect.remove(None)
        assert modifiers.triple_bonus == 0
    
    def test_score_multiplier_effect(self, modifiers):
        """Test score multiplier effect"""
        effect = ScoreMultiplierEffect(2.0)
        effect.apply(None)
        
        assert modifiers.score_multiplier == 2.0
        
        effect.remove(None)
        assert modifiers.score_multiplier == 1.0
    
    def test_stacking_score_multipliers(self, modifiers):
        """Test stacking multiple score multipliers"""
        effect1 = ScoreMultiplierEffect(2.0)
        effect2 = ScoreMultiplierEffect(1.5)
        
        effect1.apply(None)
        effect2.apply(None)
        
        assert modifiers.score_multiplier == 3.0  # 2.0 * 1.5


class TestGameplayEffects:
    """Tests for gameplay-modifying effects"""
    
    @pytest.fixture
    def modifiers(self):
        mod = GameModifiers()
        set_modifiers(mod)
        return mod
    
    def test_disable_hold_effect(self, modifiers):
        """Test hold disable effect"""
        effect = DisableHoldEffect(True)
        effect.apply(None)
        
        assert modifiers.hold_disabled == True
        
        effect.remove(None)
        assert modifiers.hold_disabled == False
    
    def test_disable_ghost_effect(self, modifiers):
        """Test ghost disable effect"""
        effect = DisableGhostEffect(True)
        effect.apply(None)
        
        assert modifiers.ghost_disabled == True
        
        effect.remove(None)
        assert modifiers.ghost_disabled == False
    
    def test_lock_delay_multiplier_effect(self, modifiers):
        """Test lock delay multiplier effect"""
        effect = LockDelayMultiplierEffect(0.5)
        effect.apply(None)
        
        assert modifiers.lock_delay_multiplier == 0.5
        
        effect.remove(None)
        assert modifiers.lock_delay_multiplier == 1.0
    
    def test_increased_lock_delay(self, modifiers):
        """Test increased lock delay effect (orange card)"""
        effect = LockDelayMultiplierEffect(3.0)
        effect.apply(None)
        
        assert modifiers.lock_delay_multiplier == 3.0


class TestComboBonusEffect:
    """Tests specifically for combo bonus effect"""
    
    @pytest.fixture
    def modifiers(self):
        mod = GameModifiers()
        set_modifiers(mod)
        return mod
    
    def test_combo_bonus_applies(self, modifiers):
        """Test combo bonus is added to list"""
        effect = ComboBonusEffect(min_combo=4, multiplier_bonus=3.0)
        effect.apply(None)
        
        assert len(modifiers.combo_bonuses) == 1
        assert modifiers.combo_bonuses[0]["min_combo"] == 4
        assert modifiers.combo_bonuses[0]["multiplier_bonus"] == 3.0
    
    def test_combo_bonus_removal(self, modifiers):
        """Test combo bonus is removed"""
        effect = ComboBonusEffect(min_combo=4, multiplier_bonus=3.0)
        effect.apply(None)
        effect.remove(None)
        
        assert len(modifiers.combo_bonuses) == 0
    
    def test_multiple_combo_bonuses(self, modifiers):
        """Test multiple combo bonuses stack"""
        effect1 = ComboBonusEffect(min_combo=3, multiplier_bonus=2.0)
        effect2 = ComboBonusEffect(min_combo=5, multiplier_bonus=5.0)
        
        effect1.apply(None)
        effect2.apply(None)
        
        # At combo 5, both should apply
        total = modifiers.get_total_combo_bonus(5)
        assert total == 7.0  # 2.0 + 5.0


class TestScoreCalculation:
    """Tests for final score calculation with modifiers"""
    
    @pytest.fixture
    def modifiers(self):
        mod = GameModifiers()
        set_modifiers(mod)
        return mod
    
    def test_basic_score(self, modifiers):
        """Test basic score without modifiers"""
        score = modifiers.calculate_final_score(
            base_score=100,
            lines_cleared=1,
            is_tetris=False,
            is_b2b=False,
            combo_count=0
        )
        assert score == 100
    
    def test_score_with_line_bonus(self, modifiers):
        """Test score with line bonus"""
        modifiers.line_bonus = 50
        score = modifiers.calculate_final_score(
            base_score=100,
            lines_cleared=2,
            is_tetris=False,
            is_b2b=False,
            combo_count=0
        )
        assert score == 200  # 100 + 2*50
    
    def test_score_with_double_bonus(self, modifiers):
        """Test score with double line bonus"""
        modifiers.double_bonus = 200
        score = modifiers.calculate_final_score(
            base_score=300,
            lines_cleared=2,
            is_tetris=False,
            is_b2b=False,
            combo_count=0
        )
        assert score == 500  # 300 + 200
    
    def test_score_with_tetris_bonus(self, modifiers):
        """Test score with Tetris bonus"""
        modifiers.tetris_bonus = 0.5
        score = modifiers.calculate_final_score(
            base_score=800,
            lines_cleared=4,
            is_tetris=True,
            is_b2b=False,
            combo_count=0
        )
        assert score == 1200  # 800 * 1.5
    
    def test_score_with_b2b_bonus(self, modifiers):
        """Test score with Back-to-Back bonus"""
        modifiers.b2b_bonus = 1.0
        score = modifiers.calculate_final_score(
            base_score=800,
            lines_cleared=4,
            is_tetris=True,
            is_b2b=True,
            combo_count=0
        )
        assert score == 1600  # 800 * 2.0
    
    def test_score_with_multiplier(self, modifiers):
        """Test score with global multiplier"""
        modifiers.score_multiplier = 2.0
        score = modifiers.calculate_final_score(
            base_score=100,
            lines_cleared=1,
            is_tetris=False,
            is_b2b=False,
            combo_count=0
        )
        assert score == 200  # 100 * 2.0
    
    def test_combined_modifiers(self, modifiers):
        """Test score with multiple modifiers"""
        modifiers.line_bonus = 50
        modifiers.tetris_bonus = 0.5
        modifiers.score_multiplier = 1.5
        
        score = modifiers.calculate_final_score(
            base_score=800,
            lines_cleared=4,
            is_tetris=True,
            is_b2b=False,
            combo_count=0
        )
        # (800 + 4*50) * 1.5 (tetris) * 1.5 (multiplier) = 1000 * 1.5 * 1.5 = 2250
        assert score == 2250



