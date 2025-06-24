Chess Game with AI and Learning Module

This project is an interactive Chess Game implemented in Python, featuring a playable AI that improves its moves over time using a learning mechanism. It is built with Tkinter for the user interface, PIL for piece rendering, and JSON-based caching for move learning.

Features

Two-Player Game: Play against another human or the AI.

Learning AI: The AI records moves and outcomes, adapting its strategies over time.

Move Validation: Supports complex moves, including en passant and pawn promotion.

Checkmate Detection: Alerts when the game has been won.

Lightweight Architecture: Pure Python and Tkinter implementation.

Getting Started

Prerequisites

Python 3.9 or later

PIL (Pillow) for image processing

Install Dependencies

pip install pillow

Usage

python path/to/your/script.py

Directory Structure

images/: Directory for piece images (w_king.png, b_queen.png, etc.)

learning_cache.json: Created automatically to save AI move data.

Features to Expand

Advanced AI using deep learning techniques.

Multiplayer over the network.

Opening and endgame databases.

Contributing

Feel free to open issues, make suggestions, or fork this project to help evolve the AI or add new game features!

License

This project is open source and available under the MIT License.

Future Vision: This project aims to evolve into a robust, learning chess engine that can adapt to its opponent and provide a challenging experience for both casual and competitive players.

Have fun and happy coding!

