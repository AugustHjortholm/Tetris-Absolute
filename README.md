# Tetris Roguelike

A standalone Tetris game with roguelike attributes, built with Python and Pygame. Designed with **low coupling** architecture for maximum extensibility.

## Features

- ✅ Full Tetris implementation with modern mechanics
- ✅ Standalone executable (no browser required)
- ✅ Clean interface-based architecture
- ✅ Easy to extend with roguelike modifiers
- ✅ Beautiful Pygame graphics

## Architecture

The project uses **Abstract Base Classes (ABC)** to define clear interfaces between components. This makes it trivial to swap implementations or add new behaviors for roguelike features.

### Core Interfaces

- **IBoard** - Game board (add obstacles, special cells, different sizes)
- **IPiece** - Tetris pieces (add special pieces, power-ups)
- **IPieceGenerator** - Piece generation (weighted random, specific sequences)
- **IGameState** - Game state management (add roguelike stats, buffs)
- **IRenderer** - Rendering system (swap graphics, add effects)
- **IInputHandler** - Input handling (keyboard, gamepad, AI, network)
- **IScoringSystem** - Scoring rules (multipliers, combos, special bonuses)

### Standard Implementations

Located in the `implementations/` directory:
- `StandardBoard` - Classic 10x20 Tetris board
- `StandardPiece` - 7 standard tetrominoes (I, J, L, O, S, T, Z)
- `SevenBagGenerator` - Modern Tetris randomization (fair distribution)
- `PygameRenderer` - Beautiful Pygame graphics
- `KeyboardInputHandler` - Responsive keyboard controls with DAS
- `StandardScoringSystem` - Classic Tetris scoring

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Setup

1. **Clone or download this project**

2. **Create a virtual environment (recommended):**

```bash
python -m venv venv
```

3. **Activate the virtual environment:**

Windows:
```bash
venv\Scripts\activate
```

Mac/Linux:
```bash
source venv/bin/activate
```

4. **Install dependencies:**

```bash
pip install -r requirements.txt
```

## Testing

Run the unit test suite:

```bash
pytest tests/ -v
```

All 52 tests should pass. See `tests/README.md` for more details.

## Running the Game

```bash
python main.py
```

## Controls

### Keyboard

- **← →** - Move piece left/right (one press = one move)
- **A / Z** - Rotate counter-clockwise
- **D** - Rotate clockwise
- **↑** - Soft drop (hold for continuous drop)
- **↓** - Hard drop (instant drop)
- **P** or **Escape** - Pause
- **R** - Restart game

### Controller (Auto-detected)

**Tested:** PlayStation 5 DualSense  
**Should work:** Xbox controllers (untested)

**Primary Controls:**
- **D-Pad Left** - Move piece left
- **D-Pad Right** - Move piece right
- **Square / X (Xbox)** - Rotate clockwise
- **Cross (X) / A (Xbox)** - Rotate counter-clockwise
- **D-Pad Down** - Soft drop (hold for continuous drop)
- **D-Pad Up** - Hard drop (instant drop)
- **Options / Start / Triangle / Y** - Pause
- **Share / Back** - Restart

**Alternative Controls:**
- **Left Stick** - Can be used for movement and soft drop
- **L1 / LB** - Rotate counter-clockwise
- **R1 / RB** - Rotate clockwise

The game will automatically detect and use your controller if connected. Otherwise, it falls back to keyboard controls.

## Creating an Executable

To create a standalone `.exe` file (Windows) or executable (Mac/Linux):

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name TetrisRoguelike main.py
```

The executable will be in the `dist/` folder.

## Adding Roguelike Features

The architecture makes it **incredibly easy** to add roguelike modifiers. Here are some examples:

### Example 1: Weighted Piece Generator

```python
# implementations/weighted_generator.py
from core.interfaces import IPieceGenerator

class WeightedGenerator(IPieceGenerator):
    """Favors certain pieces based on weights"""
    
    def __init__(self, weights: dict):
        self.weights = weights
        # Your implementation here
```

Then swap it in `main.py`:
```python
piece_generator = WeightedGenerator({'I': 0.3, 'O': 0.1, ...})
```

### Example 2: Board with Obstacles

```python
# implementations/obstacle_board.py
from implementations.standard_board import StandardBoard

class ObstacleBoard(StandardBoard):
    """Board with random obstacles"""
    
    def __init__(self, obstacle_density=0.1):
        super().__init__()
        self._place_random_obstacles(obstacle_density)
```

### Example 3: Special Scoring System

```python
# implementations/combo_scoring.py
from core.interfaces import IScoringSystem

class ComboScoringSystem(IScoringSystem):
    """Adds combo multipliers"""
    
    def calculate_score(self, lines_cleared, level, soft_drop=0, hard_drop=0):
        base_score = super().calculate_score(...)
        return base_score * self.combo_multiplier
```

Just swap the implementation in `main.py` - **no other code needs to change!**

## Project Structure

```
tetris-roguelike/
├── core/
│   └── interfaces.py          # All interface definitions (ABCs)
├── implementations/
│   ├── standard_board.py
│   ├── standard_piece.py
│   ├── seven_bag_generator.py
│   ├── standard_game_state.py
│   ├── pygame_renderer.py
│   ├── keyboard_input_handler.py
│   └── standard_scoring_system.py
├── game.py                    # Main game controller
├── main.py                    # Entry point & dependency injection
├── requirements.txt
└── README.md
```

## Next Steps for Roguelike Features

Here are some ideas for extending the game:

1. **Power-up System** - Create special pieces that grant abilities
2. **Obstacle Generation** - Random blocked cells that appear
3. **Variable Board Sizes** - Different sized boards as modifiers
4. **Piece Mutations** - Pieces that change shape mid-game
5. **Special Abilities** - Time slow, line clear, piece preview
6. **Roguelike Progression** - Unlock modifiers between runs
7. **Meta-progression** - Permanent upgrades

## Why Python?

- ✅ Easy to learn and modify (great for rapid prototyping)
- ✅ Pygame is perfect for 2D games
- ✅ ABC system maintains clean interfaces
- ✅ Can be compiled to standalone .exe
- ✅ Large community and great libraries
- ✅ Fast iteration for adding features

## License

MIT

## Contributing

Feel free to extend this game with roguelike features! The architecture is designed to make adding new mechanics as easy as possible.
