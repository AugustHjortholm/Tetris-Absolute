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
from implementations.standard_scoring_system import StandardScoringSystem


def main():
    """Main entry point"""
    # Initialize Pygame
    pygame.init()
    
    # Create window
    window_width = 600
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
    renderer = PygameRenderer(screen, cell_size=30)
    input_handler = KeyboardInputHandler()
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
    
    print("Game started!")
    print("Controls:")
    print("  Left/Right Arrows: Move piece")
    print("  A/D: Rotate left/right")
    print("  Up Arrow: Soft drop (faster fall)")
    print("  Down Arrow: Hard drop (instant)")
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

