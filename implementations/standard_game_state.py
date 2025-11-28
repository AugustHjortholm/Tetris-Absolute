"""
Standard game state implementation.
"""

from core.interfaces import IGameState


class StandardGameState(IGameState):
    """Standard implementation of game state"""
    
    def __init__(self):
        self._score = 0
        self._level = 1
        self._lines = 0
        self._is_game_over = False
        self._is_paused = False
    
    @property
    def score(self) -> int:
        return self._score
    
    @property
    def level(self) -> int:
        return self._level
    
    @property
    def lines(self) -> int:
        return self._lines
    
    @property
    def is_game_over(self) -> bool:
        return self._is_game_over
    
    @property
    def is_paused(self) -> bool:
        return self._is_paused
    
    def add_score(self, points: int) -> None:
        self._score += points
    
    def add_lines(self, count: int) -> None:
        self._lines += count
    
    def increment_level(self) -> None:
        self._level += 1
    
    def pause(self) -> None:
        self._is_paused = True
    
    def resume(self) -> None:
        self._is_paused = False
    
    def set_game_over(self, game_over: bool) -> None:
        self._is_game_over = game_over
    
    def reset(self) -> None:
        self._score = 0
        self._level = 1
        self._lines = 0
        self._is_game_over = False
        self._is_paused = False

