"""
Main entry point for Tetris Roguelike.
This is where we wire up all the dependencies (dependency injection).
"""

import pygame
from game import Game
from menu import MainMenu, MenuState
from card_collection_menu import CardCollectionMenu
from implementations.standard_board import StandardBoard
from implementations.seven_bag_generator import SevenBagGenerator
from implementations.standard_game_state import StandardGameState
from implementations.pygame_renderer import PygameRenderer
from implementations.keyboard_input_handler import KeyboardInputHandler
from implementations.controller_input_handler import ControllerInputHandler
from implementations.standard_scoring_system import StandardScoringSystem
from implementations.card_renderer import CardRenderer


def create_game(screen, use_controller: bool) -> Game:
    """Create a new game instance with all dependencies"""
    board = StandardBoard(width=10, height=20)
    piece_generator = SevenBagGenerator()
    game_state = StandardGameState()
    
    if use_controller:
        input_handler = ControllerInputHandler()
    else:
        input_handler = KeyboardInputHandler()
    
    renderer = PygameRenderer(screen, cell_size=30, use_controller=use_controller)
    scoring_system = StandardScoringSystem()
    
    # Create card renderer for roguelike card selection
    card_renderer = CardRenderer(screen)
    
    game = Game(
        board=board,
        piece_generator=piece_generator,
        game_state=game_state,
        renderer=renderer,
        input_handler=input_handler,
        scoring_system=scoring_system
    )
    
    # Attach card renderer to game
    game.card_renderer = card_renderer
    
    return game


def run_game(screen, clock, fps: int, use_controller: bool):
    """Run a game session. Returns True if should return to menu, False to quit."""
    game = create_game(screen, use_controller)
    game.start()
    
    print("\nGame started!")
    
    # Main game loop
    running = True
    while running:
        # Handle input
        running = game.handle_input()
        
        # Check if game requested return to menu
        if game.return_to_menu:
            return True  # Return to menu
        
        # Update game state
        game.update()
        
        # Render
        game.render()
        
        # Control framerate
        clock.tick(fps)
    
    return False  # Quit entirely


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
    
    # Auto-detect controller or use keyboard
    use_controller = ControllerInputHandler.is_controller_connected()
    
    if use_controller:
        print("\n=== Controller Mode ===")
        controller = ControllerInputHandler()
        print(f"Controller: {controller.controller_name}")
    else:
        print("\n=== Keyboard Mode ===")
    
    # Main application loop
    running = True
    while running:
        # Show main menu
        menu = MainMenu(screen)
        menu_result = menu.run()
        
        if menu_result == MenuState.IN_GAME:
            # Run the game
            return_to_menu = run_game(screen, clock, fps, use_controller)
            if not return_to_menu:
                running = False
        elif menu_result == MenuState.CARD_COLLECTION:
            # Show card collection menu
            collection_menu = CardCollectionMenu(screen)
            collection_menu.run()
            # Returns to main menu after
        else:
            # Menu was exited (quit)
            running = False
    
    # Clean up
    pygame.quit()
    print("\nThanks for playing!")


if __name__ == "__main__":
    main()
