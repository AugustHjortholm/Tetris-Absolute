"""
Tests for the main menu system.
Tests menu config, state management, and navigation.
"""

import pytest
from config import game_config, localization


class TestMenuConfig:
    """Tests for menu configuration loading"""
    
    def test_menu_config_exists(self):
        """Test that menu config section exists"""
        assert game_config.menu is not None
        assert isinstance(game_config.menu, dict)
    
    def test_menu_colors_exist(self):
        """Test that all menu colors are defined"""
        colors = [
            "background",
            "title", 
            "text",
            "selected",
            "disabled",
            "button_background",
            "button_hover",
            "button_border",
            "grid_line",
            "grid_highlight"
        ]
        for color_name in colors:
            color = game_config.get_menu_color(color_name)
            assert isinstance(color, tuple)
            assert len(color) == 3
    
    def test_menu_background_color(self):
        """Test menu background color"""
        bg = game_config.get_menu_color("background")
        # Should be dark purple (#0F0A23)
        assert bg == (15, 10, 35)
    
    def test_menu_title_color(self):
        """Test menu title color is cyan"""
        title = game_config.get_menu_color("title")
        assert title == (0, 255, 255)
    
    def test_menu_selected_color(self):
        """Test menu selected color is gold"""
        selected = game_config.get_menu_color("selected")
        assert selected == (255, 215, 0)
    
    def test_menu_grid_cell_size(self):
        """Test menu grid cell size"""
        cell_size = game_config.menu_grid_cell_size
        assert cell_size == 60
    
    def test_menu_input_cooldown(self):
        """Test menu input cooldown is in seconds"""
        cooldown = game_config.menu_input_cooldown
        assert cooldown == 0.2  # 200ms = 0.2s
    
    def test_menu_version_string(self):
        """Test menu version string exists"""
        version = game_config.menu_version
        assert isinstance(version, str)
        assert "v" in version.lower()


class TestMenuLocalization:
    """Tests for menu text localization"""
    
    def test_game_title(self):
        """Test game title text"""
        title = localization.get("game", "title")
        assert title == "TETRIS"
    
    def test_game_subtitle(self):
        """Test game subtitle text"""
        subtitle = localization.get("game", "subtitle")
        assert subtitle == "ROGUELIKE"
    
    def test_menu_items_text(self):
        """Test all menu item text exists"""
        menu_items = ["new_game", "custom_game", "challenges", "options", "exit"]
        for item in menu_items:
            text = localization.get("menu", item)
            assert isinstance(text, str)
            assert len(text) > 0
    
    def test_new_game_text(self):
        """Test new game button text"""
        text = localization.get("menu", "new_game")
        assert text == "NEW GAME"
    
    def test_exit_text(self):
        """Test exit button text"""
        text = localization.get("menu", "exit")
        assert text == "EXIT"
    
    def test_coming_soon_text(self):
        """Test coming soon text for disabled items"""
        text = localization.get("menu", "coming_soon")
        assert text == "Coming Soon"
    
    def test_menu_controls_keyboard(self):
        """Test keyboard controls text for menu"""
        text = localization.get("menu", "controls_keyboard")
        assert "Arrow Keys" in text
        assert "Enter" in text
    
    def test_menu_controls_controller(self):
        """Test controller controls text for menu"""
        text = localization.get("menu", "controls_controller")
        assert "D-Pad" in text


class TestMenuStateEnum:
    """Tests for MenuState enum"""
    
    def test_menu_state_import(self):
        """Test that MenuState can be imported"""
        from menu import MenuState
        assert MenuState is not None
    
    def test_menu_states_exist(self):
        """Test that all menu states exist"""
        from menu import MenuState
        
        assert hasattr(MenuState, 'MAIN_MENU')
        assert hasattr(MenuState, 'IN_GAME')
        assert hasattr(MenuState, 'CUSTOM_GAME')
        assert hasattr(MenuState, 'CHALLENGES')
        assert hasattr(MenuState, 'OPTIONS')


class TestMenuItemClass:
    """Tests for MenuItem class"""
    
    def test_menu_item_creation(self):
        """Test creating a menu item"""
        from menu import MenuItem
        
        item = MenuItem("Test", lambda: None, True)
        assert item.text == "Test"
        assert item.enabled == True
    
    def test_menu_item_disabled(self):
        """Test disabled menu item"""
        from menu import MenuItem
        
        item = MenuItem("Disabled", None, False)
        assert item.enabled == False
    
    def test_menu_item_with_action(self):
        """Test menu item with action callback"""
        from menu import MenuItem
        
        called = [False]
        def action():
            called[0] = True
        
        item = MenuItem("Action", action, True)
        item.action()
        assert called[0] == True


class TestReturnToMenuControls:
    """Tests for return to menu control text"""
    
    def test_keyboard_menu_control(self):
        """Test keyboard menu control text"""
        text = localization.get("controls_keyboard", "menu")
        assert "R" in text
        assert "Menu" in text
    
    def test_controller_menu_control(self):
        """Test controller menu control text"""
        text = localization.get("controls_controller", "menu")
        assert "Share" in text
        assert "Menu" in text
    
    def test_game_over_menu_prompt(self):
        """Test game over screen menu prompt"""
        text = localization.get("game_states", "press_menu")
        assert "R" in text
        assert "Menu" in text


class TestGameReturnToMenu:
    """Tests for game return to menu functionality"""
    
    def test_game_has_return_to_menu_flag(self):
        """Test that Game class has return_to_menu flag"""
        # We'll check this conceptually since we can't easily instantiate Game
        # without pygame initialization
        from game import Game
        
        # Check that the class has the method
        assert hasattr(Game, 'request_menu')
    
    def test_request_menu_method_exists(self):
        """Test that request_menu method exists"""
        from game import Game
        import inspect
        
        # Check method exists
        assert 'request_menu' in dir(Game)
        
        # Check it's a method
        method = getattr(Game, 'request_menu')
        assert callable(method)

