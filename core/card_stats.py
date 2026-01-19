"""
Persistent card statistics tracker.
Saves card selection counts to a JSON file for the card collection menu.
"""

import os
import json
from typing import Dict, Any
from pathlib import Path


class CardStats:
    """Tracks how many times each card has been selected across all games"""
    
    _instance = None
    STATS_FILE = "card_stats.json"
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self._initialized = True
        self._stats_path = self._get_stats_path()
        self._stats: Dict[str, int] = {}
        self._load_stats()
    
    def _get_stats_path(self) -> Path:
        """Get the path to the stats file (in user data directory)"""
        # Store in the same directory as the game for now
        # Could be changed to AppData/Local on Windows for a proper release
        base_dir = Path(__file__).parent.parent
        return base_dir / "data" / self.STATS_FILE
    
    def _load_stats(self) -> None:
        """Load stats from file"""
        if self._stats_path.exists():
            try:
                with open(self._stats_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self._stats = data.get("card_selections", {})
            except (json.JSONDecodeError, IOError):
                self._stats = {}
        else:
            self._stats = {}
    
    def _save_stats(self) -> None:
        """Save stats to file"""
        # Ensure data directory exists
        self._stats_path.parent.mkdir(parents=True, exist_ok=True)
        
        data = {
            "card_selections": self._stats
        }
        
        try:
            with open(self._stats_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
        except IOError as e:
            print(f"Warning: Could not save card stats: {e}")
    
    def record_selection(self, card_id: str) -> None:
        """Record that a card was selected"""
        if card_id not in self._stats:
            self._stats[card_id] = 0
        self._stats[card_id] += 1
        self._save_stats()
    
    def get_selection_count(self, card_id: str) -> int:
        """Get how many times a card has been selected"""
        return self._stats.get(card_id, 0)
    
    def get_all_stats(self) -> Dict[str, int]:
        """Get all card selection stats"""
        return self._stats.copy()
    
    def get_total_selections(self) -> int:
        """Get total number of card selections"""
        return sum(self._stats.values())
    
    def reset_stats(self) -> None:
        """Reset all stats (for testing or user preference)"""
        self._stats = {}
        self._save_stats()
    
    def reload(self) -> None:
        """Reload stats from disk"""
        self._load_stats()


# Singleton accessor
_card_stats: CardStats = None


def get_card_stats() -> CardStats:
    """Get the global card stats instance"""
    global _card_stats
    if _card_stats is None:
        _card_stats = CardStats()
    return _card_stats
