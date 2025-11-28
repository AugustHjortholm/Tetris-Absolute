"""
Main entry point for Tetris Roguelike.
This is where we wire up all the dependencies (dependency injection).
"""

import pygame
from game import Game
from implementations.standard_board import StandardBoard
from implementations.seven_bag_generator import SevenBagGenerator
from implementations.standard_game_state import StandardGameState
from implementations.pygame_renderer import PygameRenderer
from implementations.keyboard_input_handler import KeyboardInputHandler
from implementations.controller_input_handler import ControllerInputHandler
from implementations.standard_scoring_system import StandardScoringSystem


def main():
    """Main entry point"""
    # Initialize Pygame
    pygame.init()
    
    # Create window (wider to accommodate hold piece panel on left)
    window_width = 780  # Extra space for hold panel
    window_height = 660
    screen = pygame.display.set_mode((window_width, window_height))
    pygame.display.set_caption("Tetris Roguelike")
    
    # Create clock for framerate control
    clock = pygame.time.Clock()
    fps = 60
    
    # Create all game components (dependency injection)
    board = StandardBoard(width=10, height=20)
    piece_generator = SevenBagGenerator()
    game_state = StandardGameState()
    
    # Auto-detect controller or use keyboard
    use_controller = ControllerInputHandler.is_controller_connected()
    
    if use_controller:
        print("\n=== Controller Mode ===")
        input_handler = ControllerInputHandler()
    else:
        print("\n=== Keyboard Mode ===")
        input_handler = KeyboardInputHandler()
    
    renderer = PygameRenderer(screen, cell_size=30, use_controller=use_controller)
    scoring_system = StandardScoringSystem()
    
    # Create the game
    game = Game(
        board=board,
        piece_generator=piece_generator,
        game_state=game_state,
        renderer=renderer,
        input_handler=input_handler,
        scoring_system=scoring_system
    )
    
    # Start the game
    game.start()
    
    print("\nGame started!")
    print("\n=== Controls ===")
    
    if isinstance(input_handler, ControllerInputHandler):
        print("Controller Controls:")
        print("  D-Pad Left: Move left")
        print("  D-Pad Right: Move right")
        print("  Square: Rotate clockwise")
        print("  Cross (X): Rotate counter-clockwise")
        print("  D-Pad Down: Soft drop (hold)")
        print("  D-Pad Up: Hard drop (instant)")
        print("  L1 / R1: Hold/Store piece")
        print("  Options / Triangle: Pause")
        print("  Share: Restart")
        print("\nAlternatives: Left Stick for movement")
    else:
        print("Keyboard Controls:")
        print("  Left/Right Arrows: Move piece")
        print("  A/Z: Rotate left")
        print("  D: Rotate right")
        print("  Up Arrow: Soft drop (hold to continuously drop)")
        print("  Down Arrow: Hard drop (instant)")
        print("  C/Shift: Hold/Store piece")
        print("  P: Pause")
        print("  R: Restart")
    
    # Main game loop
    running = True
    while running:
        # Handle input
        running = game.handle_input()
        
        # Update game state
        game.update()
        
        # Render
        game.render()
        
        # Control framerate
        clock.tick(fps)
    
    # Clean up
    pygame.quit()


if __name__ == "__main__":
    main()

