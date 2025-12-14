# Chess Game

An advanced, full-featured chess game built in Python with Pygame. Enjoy a modern, visually appealing interface, complete support for all chess rules, and a robust AI opponent powered by neural networks. The game includes detailed move history, PGN export with time tracking, and a smooth user experience for both casual and advanced players.

![Python](https://img.shields.io/badge/Python-3.13+-blue.svg)
![Pygame](https://img.shields.io/badge/Pygame-2.6+-green.svg)


## Features

- **Complete Chess Rules:** All standard chess rules, including castling, en passant, pawn promotion, check, checkmate, and stalemate.
- **Modern User Interface:** Clean Pygame-based UI with piece sprites, move highlighting, last move and check indicators, and a move history panel.
- **AI Opponent:** Play against a challenging bot or watch bot-vs-bot matches. AI powered by neural network models (PyTorch).
- **PGN Export:** Automatically saves every game in PGN format, including move times and algebraic notation.
- **Move Time Tracking:** Each move’s time is recorded and included in the PGN for detailed analysis.
- **Undo/Redo:** Freely navigate move history, even after bot moves.
- **Sound Effects:** Move, capture, and check/checkmate notifications.
- **Custom Assets:** High-quality board and piece images, with support for multiple sprite sizes.

## Advanced Features

- **PGN Export:** Automatically saves each game in PGN format, including move times and standard algebraic notation (SAN).
- **Move Time Tracking:** Each move’s time is recorded and included in the PGN. (If all times are 0.00s, check that time tracking is enabled and timestamps are updated between moves.)
- **AI Opponent:** Play against a bot, or watch bot-vs-bot matches.
- **Undo/Redo:** Navigate move history freely, including after bot moves.

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
├── main.py                # Entry point
├── pyproject.toml         # Project configuration
├── core/                  # Game logic
│   ├── __init__.py
│   ├── board.py           # Board state and game logic
│   ├── constants.py       # Constants and colors
│   ├── pieces.py          # Piece classes with movement rules
│   └── types.py           # Type definitions (Position, Move, etc.)
├── ui/                    # User interface
│   ├── __init__.py
│   ├── game.py            # Pygame rendering and input handling
│   └── game.py.original   # Backup of game.py
├── game_ai/               # AI logic
│   ├── __init__.py
│   ├── bot.py             # Bot move selection
│   ├── utils.py           # AI utilities
│   └── torch/             # Neural network models and data
│       ├── __init__.py
│       ├── lichess_elite_2020-08.pgn
│       ├── model.py
│       ├── predict.py
│       ├── utils.py
│       ├── data/
│       │   ├── test_cases.npz
│       │   ├── train_cases.npz
│       │   └── val_cases.npz
│       └── models/
│           └── chess_model.ckpt
├── logger/                # Logging utilities
│   ├── __init__.py
│   └── logger.py          # Logger implementation
├── records/               # Saved PGN game records
│   └── chess_record_*.pgn
├── assets/                # Game assets
│   ├── img/
│   │   ├── boards/            # Board images
│   │   ├── 16x16 pieces/      # Piece sprites (16x16)
│   │   ├── 16x32 pieces/      # Piece sprites (16x32)
│   │   └── README.txt
│   └── sound/
```

## Credits

- **Piece sprites and board images**: [DANI MACCARI](https://dani-maccari.itch.io/) - Free for personal and commercial use with attribution

## License

This project is open source and available under the MIT License.
