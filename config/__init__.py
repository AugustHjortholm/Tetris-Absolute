"""Configuration module for loading game settings from JSON files."""

import json
import os
from typing import Dict, Any, Tuple

# Default paths
CONFIG_DIR = os.path.dirname(os.path.abspath(__file__))
GAME_CONFIG_PATH = os.path.join(CONFIG_DIR, "game_config.json")
LANG_DIR = os.path.join(CONFIG_DIR, "lang")


def load_json(file_path: str) -> Dict[str, Any]:
    """Load a JSON file and return its contents."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
    """Convert hex color string to RGB tuple."""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


class GameConfig:
    """Manages game configuration loaded from JSON."""
    
    _instance = None
    _config = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load_config()
        return cls._instance
    
    def _load_config(self):
        """Load the game configuration from JSON file."""
        self._config = load_json(GAME_CONFIG_PATH)
    
    def reload(self):
        """Reload the configuration from disk."""
        self._load_config()
    
    # Scoring
    @property
    def base_scores(self) -> Dict[str, int]:
        return self._config["scoring"]["base_scores"]
    
    @property
    def multipliers(self) -> Dict[str, float]:
        return self._config["scoring"]["multipliers"]
    
    @property
    def drop_points(self) -> Dict[str, int]:
        return self._config["scoring"]["drop_points"]
    
    # Speed
    @property
    def speed(self) -> Dict[str, float]:
        return self._config["speed"]
    
    # Lock delay
    @property
    def lock_delay(self) -> Dict[str, float]:
        return self._config["lock_delay"]
    
    # DAS
    @property
    def das(self) -> Dict[str, int]:
        return self._config["das"]
    
    # Colors
    def get_piece_color(self, piece_type: str) -> Tuple[int, int, int]:
        """Get RGB color for a piece type."""
        hex_color = self._config["colors"]["pieces"].get(piece_type, "#FFFFFF")
        return hex_to_rgb(hex_color)
    
    def get_ui_color(self, color_name: str) -> Tuple[int, int, int]:
        """Get RGB color for a UI element."""
        hex_color = self._config["colors"]["ui"].get(color_name, "#FFFFFF")
        return hex_to_rgb(hex_color)
    
    def get_game_over_color(self, color_name: str) -> Any:
        """Get color/alpha for game over screen."""
        return self._config["colors"]["game_over"].get(color_name)
    
    def get_pause_color(self, color_name: str) -> Any:
        """Get color/alpha for pause screen."""
        return self._config["colors"]["pause"].get(color_name)
    
    # Board
    @property
    def board(self) -> Dict[str, int]:
        return self._config["board"]
    
    # Notifications
    @property
    def notification_duration(self) -> float:
        return self._config["notifications"]["duration"]
    
    # Pieces
    def get_piece_shape(self, piece_type: str) -> list:
        """Get the shape array for a piece type."""
        return self._config["pieces"][piece_type]["shape"]
    
    def get_all_piece_types(self) -> list:
        """Get list of all piece types."""
        return list(self._config["pieces"].keys())


class Localization:
    """Manages localized text loaded from JSON."""
    
    _instance = None
    _lang = None
    _current_lang = "en"
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load_lang("en")
        return cls._instance
    
    def _load_lang(self, lang_code: str):
        """Load a language file."""
        lang_path = os.path.join(LANG_DIR, f"{lang_code}.json")
        self._lang = load_json(lang_path)
        self._current_lang = lang_code
    
    def set_language(self, lang_code: str):
        """Change the current language."""
        self._load_lang(lang_code)
    
    def get(self, *keys, **kwargs) -> str:
        """
        Get a localized string by key path.
        Example: get("ui", "score") returns the score label
        Supports string formatting with kwargs.
        """
        value = self._lang
        for key in keys:
            value = value.get(key, f"[{'.'.join(keys)}]")
            if isinstance(value, str):
                break
        
        if isinstance(value, str) and kwargs:
            # Replace {key} placeholders with values
            for k, v in kwargs.items():
                value = value.replace(f"{{{k}}}", str(v))
        
        return value
    
    @property
    def current_language(self) -> str:
        return self._current_lang


# Singleton instances
game_config = GameConfig()
localization = Localization()

