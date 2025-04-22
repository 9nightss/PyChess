# ♟️ Python Tkinter Chess Game

A fully interactive chess game built with Python's `tkinter` library. Supports all standard chess rules, including **castling**, **en passant**, **promotion**, **check/checkmate detection**, and even **premoves**. Play against a human or a basic AI with randomized move selection.

## 🚀 Features

- 🧠 **Game Modes**:
  - Player vs Player (PvP)
  - Player vs AI (Randomized moves)
- ✅ **Rules Supported**:
  - Standard piece movements
  - Castling (kingside and queenside)
  - En passant
  - Pawn promotion (custom choice via dialog)
  - Check and checkmate detection
  - Stalemate detection
  - Premove system for quick gameplay
- 🎨 **UI Highlights**:
  - Tkinter-based 8x8 chessboard
  - Highlighted legal move squares
  - Semi-transparent themed piece icons
- 🔊 **Sound Effects**:
  - Play move sounds (custom `.wav` file path)

## 🖼️ Screenshots

_Add screenshots here if you like._

## 🛠️ Getting Started

### Prerequisites

- Python 3.x
- Dependencies:
  ```bash
  pip install pillow
  pip install tkinter
  pip install ctypes
  
  ```

### Folder Structure

```
chess_game/
│
├── pieces/                  # Folder containing piece images (e.g. w_pawn.png, b_king.png)
│   ├── w_pawn.png
│   ├── b_queen.png
│   └── move-self.wav        # Optional move sound effect
├── chess_game.py            # Main game script
└── README.md
```

### Running the Game

```bash
python chess_game.py
```

## 🖱️ Controls

- Click a piece to select it.
- Valid moves will be highlighted.
- Click a destination square to move.
- Promotion will prompt a dialog to choose the piece.
- For AI mode, switch the `mode` parameter in the constructor:
  ```python
  game = ChessGame(root, mode="ai")
  ```

## ⚙️ Customization

- **Piece Icons**: Replace PNGs in the `pieces/` folder.
- **Sound Effects**: Replace `move-self.wav` with your own sound.
- **AI Logic**: Currently uses randomized legal move selection. Can be replaced with a proper chess engine.

## 📦 Future Improvements

- Add undo/redo functionality
- Timer support
- Advanced AI (minimax or Stockfish integration)
- Online multiplayer
- Move history tracker

## 📄 License

MIT License — use freely, modify, and share.
