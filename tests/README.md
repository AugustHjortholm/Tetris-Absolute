# Unit Tests

This directory contains unit tests for the Tetris Roguelike game.

## Running Tests

### Install pytest

```bash
pip install pytest
```

### Run all tests

```bash
pytest tests/ -v
```

### Run specific test file

```bash
pytest tests/test_board.py -v
```

### Run specific test

```bash
pytest tests/test_board.py::TestStandardBoard::test_clear_multiple_rows -v
```

## Test Coverage

### test_board.py
Tests for the game board implementation:
- Board initialization and dimensions
- Cell get/set operations
- Piece placement and collision detection
- Line detection (single, multiple, non-consecutive)
- **Line clearing (multiple rows at once)** - Fixed bug where only one line cleared at a time
- Board cloning

### test_piece.py
Tests for piece implementations:
- Piece creation and properties
- Rotation (clockwise and counter-clockwise)
- Piece cloning
- PieceFactory for all 7 standard tetrominoes

### test_piece_generator.py
Tests for the 7-bag random generator:
- Piece generation
- Peek functionality
- Fair distribution (all 7 pieces in each bag)
- Randomization
- Generator reset

### test_game_state.py
Tests for game state management:
- Score, level, and lines tracking
- Pause/resume functionality
- Game over state
- State reset

### test_scoring_system.py
Tests for scoring calculations:
- Line clear scoring (1, 2, 3, 4 lines)
- Soft drop and hard drop points
- Level progression
- Drop speed calculation

## Bug Fixes Verified by Tests

### Multiple Line Clear Bug (Fixed)
**Issue**: When clearing multiple rows at once (e.g., Tetris with 4 lines), only one line would clear, and the next would clear on the following move.

**Root Cause**: The `clear_rows()` method was inserting empty rows at the top one at a time inside the loop, causing index shifting issues.

**Fix**: Modified to delete all rows first, then insert all empty rows at once.

**Tests**: `test_clear_multiple_rows`, `test_clear_non_consecutive_rows`, `test_clear_four_rows_tetris`

