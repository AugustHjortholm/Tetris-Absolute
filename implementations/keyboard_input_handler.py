"""
Keyboard input handler using Pygame.
"""

import pygame
from core.interfaces import IInputHandler


class KeyboardInputHandler(IInputHandler):
    """Pygame keyboard input handler"""
    
    def __init__(self):
        # One-shot actions (only trigger once per key press)
        self._move_left = False
        self._move_right = False
        self._hard_drop = False
        self._rotate_left = False
        self._rotate_right = False
        self._pause = False
        self._restart = False
        self._hold = False
        
        # Continuous actions (trigger while held)
        self._soft_drop_held = False
    
    def poll_events(self) -> bool:
        """Poll for events. Returns False if quit event detected."""
        # Reset all one-shot actions at the start of each frame
        self._move_left = False
        self._move_right = False
        self._hard_drop = False
        self._rotate_left = False
        self._rotate_right = False
        self._pause = False
        self._restart = False
        self._hold = False
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            elif event.type == pygame.KEYDOWN:
                # Left/Right arrows - move piece
                if event.key == pygame.K_LEFT:
                    self._move_left = True
                
                elif event.key == pygame.K_RIGHT:
                    self._move_right = True
                
                # A/D - rotate left/right
                elif event.key in (pygame.K_a, pygame.K_z):
                    self._rotate_left = True
                
                elif event.key == pygame.K_d:
                    self._rotate_right = True
                
                # Up arrow - soft drop (continuous while held)
                elif event.key == pygame.K_UP:
                    self._soft_drop_held = True
                
                # Down arrow - hard drop
                elif event.key == pygame.K_DOWN:
                    self._hard_drop = True
                
                # Pause
                elif event.key in (pygame.K_p, pygame.K_ESCAPE):
                    self._pause = True
                
                # Restart
                elif event.key == pygame.K_r:
                    self._restart = True
                
                # Hold/Store piece
                elif event.key in (pygame.K_c, pygame.K_LSHIFT, pygame.K_RSHIFT):
                    self._hold = True
            
            elif event.type == pygame.KEYUP:
                # Stop soft drop when key released
                if event.key == pygame.K_UP:
                    self._soft_drop_held = False
        
        return True
    
    def should_move_left(self) -> bool:
        """Check if should move left (one press = one move)"""
        return self._move_left
    
    def should_move_right(self) -> bool:
        """Check if should move right (one press = one move)"""
        return self._move_right
    
    def should_move_down(self) -> bool:
        """Check if should soft drop (move down faster) - continuous while held"""
        return self._soft_drop_held
    
    def should_rotate(self) -> bool:
        """Check if should rotate clockwise"""
        return self._rotate_right
    
    def should_rotate_left(self) -> bool:
        """Check if should rotate counter-clockwise"""
        return self._rotate_left
    
    def should_hard_drop(self) -> bool:
        """Check if should hard drop (instant drop)"""
        return self._hard_drop
    
    def should_pause(self) -> bool:
        """Check if should pause"""
        return self._pause
    
    def should_restart(self) -> bool:
        """Check if should restart"""
        return self._restart
    
    def should_hold(self) -> bool:
        """Check if should hold/store piece"""
        return self._hold

