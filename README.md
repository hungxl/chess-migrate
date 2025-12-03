# Chess Game

A complete chess game built with Python and Pygame, featuring all standard chess rules and a clean user interface.

![Python](https://img.shields.io/badge/Python-3.13+-blue.svg)
![Pygame](https://img.shields.io/badge/Pygame-2.6+-green.svg)

## Features

### Complete Chess Rules
- All piece movements (Pawn, Rook, Knight, Bishop, Queen, King)
- **Castling** (kingside and queenside)
- **En passant** capture
- **Pawn promotion** with piece selection UI
- **Check, Checkmate, and Stalemate** detection

### User Interface
- Visual board with piece sprites
- **Move highlighting** - shows valid moves for selected piece
- **Last move indicator** - highlights the previous move
- **Check indicator** - red highlight on king when in check
- **Move history panel** - displays all moves in algebraic notation
- **Undo/Redo** - navigate through move history

### Sound Effects
- Move sounds
- Capture sounds
- Check/Checkmate notifications

## Installation

### Prerequisites
- Python 3.13 or higher
- [uv](https://docs.astral.sh/uv/) package manager (recommended)

### Setup

1. Clone the repository:
```bash
git clone https://github.com/hungxl/Chess.git
cd Chess
```

2. Install dependencies:
```bash
uv sync
```

## Usage

Run the game:
```bash
uv run python main.py
```

### Controls

| Action | Control |
|--------|---------|
| Select/Move piece | Left click |
| Undo | `Ctrl+Z` or `←` or `<` button |
| Redo | `Ctrl+Y` or `→` or `>` button |
| Undo all | `Ctrl+Shift+Z` or `Home` or `<<` button |
| Redo all | `Ctrl+Shift+Y` or `End` or `>>` button |
| Reset game | `R` |
| Scroll move history | Mouse wheel |

## Project Structure

```
Chess/
├── main.py              # Entry point
├── pyproject.toml       # Project configuration
├── core/                # Game logic
│   ├── __init__.py
│   ├── constants.py     # Constants and colors
│   ├── types.py         # Type definitions (Position, Move, etc.)
│   ├── pieces.py        # Piece classes with movement rules
│   └── board.py         # Board state and game logic
├── ui/                  # User interface
│   ├── __init__.py
│   └── game.py          # Pygame rendering and input handling
└── assets/              # Game assets
    ├── img/
    │   ├── boards/      # Board images
    │   └── 16x32 pieces/# Piece sprites
    └── sound/           # Sound effects
```

## Credits

- **Piece sprites and board images**: [DANI MACCARI](https://dani-maccari.itch.io/) - Free for personal and commercial use with attribution

## License

This project is open source and available under the MIT License.
