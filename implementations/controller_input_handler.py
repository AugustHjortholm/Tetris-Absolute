"""
Controller/Gamepad input handler using Pygame.
Supports PlayStation 5 (DualSense) and Xbox controllers.

Note: Xbox controller support is untested as no Xbox controller was available during development.
"""

import pygame
from core.interfaces import IInputHandler


class ControllerInputHandler(IInputHandler):
    """
    Pygame controller/gamepad input handler.
    
    Tested with: PlayStation 5 DualSense controller
    Should work with: Xbox controllers (untested)
    """
    
    # Button mappings for different controller types
    # PS5 DualSense / PS4 DualShock mapping
    PS_CROSS = 0      # X button (cross)
    PS_CIRCLE = 1     # O button (circle)
    PS_SQUARE = 2     # □ button (square)
    PS_TRIANGLE = 3   # △ button (triangle)
    PS_SHARE = 4      # Share button
    PS_PS = 5         # PS button
    PS_OPTIONS = 6    # Options button
    PS_L3 = 7         # Left stick press
    PS_R3 = 8         # Right stick press
    PS_L1 = 9         # Left bumper
    PS_R1 = 10        # Right bumper
    PS_DPAD_UP = 11
    PS_DPAD_DOWN = 12
    PS_DPAD_LEFT = 13
    PS_DPAD_RIGHT = 14
    
    # Xbox controller mapping (untested)
    XBOX_A = 0
    XBOX_B = 1
    XBOX_X = 2
    XBOX_Y = 3
    XBOX_BACK = 4
    XBOX_GUIDE = 5
    XBOX_START = 6
    XBOX_LS = 7       # Left stick press
    XBOX_RS = 8       # Right stick press
    XBOX_LB = 9       # Left bumper
    XBOX_RB = 10      # Right bumper
    XBOX_DPAD_UP = 11
    XBOX_DPAD_DOWN = 12
    XBOX_DPAD_LEFT = 13
    XBOX_DPAD_RIGHT = 14
    
    def __init__(self):
        # Initialize joystick subsystem
        pygame.joystick.init()
        
        self.controller = None
        self.controller_name = ""
        
        # Try to find and initialize a controller
        if pygame.joystick.get_count() > 0:
            self.controller = pygame.joystick.Joystick(0)
            self.controller.init()
            self.controller_name = self.controller.get_name().lower()
            print(f"Controller detected: {self.controller.get_name()}")
            
            # Detect controller type
            if "playstation" in self.controller_name or "dualsense" in self.controller_name or "ps5" in self.controller_name or "ps4" in self.controller_name:
                print("  > PlayStation controller mapping activated")
                self.is_playstation = True
            elif "xbox" in self.controller_name or "xinput" in self.controller_name:
                print("  > Xbox controller mapping activated (untested)")
                self.is_playstation = False
            else:
                print("  > Unknown controller, using PlayStation mapping as default")
                self.is_playstation = True
        else:
            print("Warning: No controller detected. Please connect a controller.")
        
        # Action states
        self._move_left = False
        self._move_right = False
        self._hard_drop = False
        self._rotate_left = False
        self._rotate_right = False
        self._pause = False
        self._restart = False
        
        # Continuous action
        self._soft_drop_held = False
        
        # D-pad tracking for one-press behavior
        self._dpad_left_pressed = False
        self._dpad_right_pressed = False
    
    def poll_events(self) -> bool:
        """Poll for events. Returns False if quit event detected."""
        if not self.controller:
            return True  # No controller, keep running
        
        # Reset one-shot actions
        self._move_left = False
        self._move_right = False
        self._hard_drop = False
        self._rotate_left = False
        self._rotate_right = False
        self._pause = False
        self._restart = False
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            elif event.type == pygame.JOYBUTTONDOWN:
                button = event.button
                
                # D-pad left - move left
                if button == self.PS_DPAD_LEFT:
                    if not self._dpad_left_pressed:
                        self._move_left = True
                        self._dpad_left_pressed = True
                
                # D-pad right - move right
                elif button == self.PS_DPAD_RIGHT:
                    if not self._dpad_right_pressed:
                        self._move_right = True
                        self._dpad_right_pressed = True
                
                # D-pad up - hard drop
                elif button == self.PS_DPAD_UP:
                    self._hard_drop = True
                
                # D-pad down - soft drop (hold to continuously drop)
                elif button == self.PS_DPAD_DOWN:
                    self._soft_drop_held = True
                
                # Square - rotate clockwise
                elif button == self.PS_SQUARE:
                    self._rotate_right = True
                
                # Cross (X) - rotate counter-clockwise
                elif button == self.PS_CROSS:
                    self._rotate_left = True
                
                # L1/R1 - alternative rotate buttons (kept for convenience)
                elif button == self.PS_L1:
                    self._rotate_left = True
                
                elif button == self.PS_R1:
                    self._rotate_right = True
                
                # Options - pause
                elif button == self.PS_OPTIONS:
                    self._pause = True
                
                # Share - restart
                elif button == self.PS_SHARE:
                    self._restart = True
                
                # Triangle - pause (alternative)
                elif button == self.PS_TRIANGLE:
                    self._pause = True
            
            elif event.type == pygame.JOYBUTTONUP:
                button = event.button
                
                # Release D-pad tracking
                if button == self.PS_DPAD_LEFT:
                    self._dpad_left_pressed = False
                
                elif button == self.PS_DPAD_RIGHT:
                    self._dpad_right_pressed = False
                
                # Stop soft drop when D-pad down released
                elif button == self.PS_DPAD_DOWN:
                    self._soft_drop_held = False
            
            elif event.type == pygame.JOYAXISMOTION:
                # Left stick for movement (alternative to D-pad)
                if event.axis == 0:  # Left stick horizontal
                    # Deadzone
                    if abs(event.value) < 0.5:
                        pass
                    elif event.value < -0.5:  # Left
                        if not self._dpad_left_pressed:
                            self._move_left = True
                            self._dpad_left_pressed = True
                    elif event.value > 0.5:  # Right
                        if not self._dpad_right_pressed:
                            self._move_right = True
                            self._dpad_right_pressed = True
                elif event.axis == 1:  # Left stick vertical
                    # Deadzone and soft drop on left stick down
                    if abs(event.value) < 0.5:
                        self._soft_drop_held = False
                    elif event.value > 0.5:  # Down (hold for soft drop)
                        self._soft_drop_held = True
                    elif event.value < -0.5:  # Up (hard drop - one shot)
                        self._hard_drop = True
            
            elif event.type == pygame.JOYHATMOTION:
                # Hat/D-pad motion (some controllers use this instead of buttons)
                hat_x, hat_y = event.value
                
                if hat_x < 0:  # Left
                    if not self._dpad_left_pressed:
                        self._move_left = True
                        self._dpad_left_pressed = True
                elif hat_x > 0:  # Right
                    if not self._dpad_right_pressed:
                        self._move_right = True
                        self._dpad_right_pressed = True
                else:
                    self._dpad_left_pressed = False
                    self._dpad_right_pressed = False
                
                if hat_y > 0:  # Up (hard drop)
                    self._hard_drop = True
                elif hat_y < 0:  # Down (soft drop - hold)
                    self._soft_drop_held = True
                else:
                    self._soft_drop_held = False
        
        return True
    
    def should_move_left(self) -> bool:
        """Check if should move left"""
        return self._move_left
    
    def should_move_right(self) -> bool:
        """Check if should move right"""
        return self._move_right
    
    def should_move_down(self) -> bool:
        """Check if should soft drop (continuous while held)"""
        return self._soft_drop_held
    
    def should_rotate(self) -> bool:
        """Check if should rotate clockwise"""
        return self._rotate_right
    
    def should_rotate_left(self) -> bool:
        """Check if should rotate counter-clockwise"""
        return self._rotate_left
    
    def should_hard_drop(self) -> bool:
        """Check if should hard drop"""
        return self._hard_drop
    
    def should_pause(self) -> bool:
        """Check if should pause"""
        return self._pause
    
    def should_restart(self) -> bool:
        """Check if should restart"""
        return self._restart
    
    @staticmethod
    def is_controller_connected() -> bool:
        """Check if any controller is connected"""
        pygame.joystick.init()
        return pygame.joystick.get_count() > 0

