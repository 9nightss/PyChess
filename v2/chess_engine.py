import tkinter as tk
from tkinter import messagebox
from tkinter import PhotoImage
import random

BOARD_SIZE = 8
SQUARE_SIZE = 80

class Move:
    def __init__(self, start, end, piece_moved):
        self.start_row, self.start_col = start
        self.end_row, self.end_col = end
        self.piece_moved = piece_moved

class GameState:
    def __init__(self, board):
        self.board = board
        self.side_to_move = 'w'

    def switch_side(self):
        self.side_to_move = 'b' if self.side_to_move == 'w' else 'w'

class ChessEngine:
    def __init__(self, game_state):
        self.gs = game_state

    def get_valid_moves(self):
        moves = []
        for r in range(8):
            for c in range(8):
                piece = self.gs.board[r][c]
                if piece == f"{self.gs.side_to_move}_pawn":
                    dir = -1 if self.gs.side_to_move == 'w' else 1
                    if 0 <= r + dir < 8 and self.gs.board[r + dir][c] == "":
                        moves.append(Move((r, c), (r + dir, c), piece))
        return moves

    def make_move(self, move):
        self.gs.board[move.start_row][move.start_col] = ""
        self.gs.board[move.end_row][move.end_col] = move.piece_moved
        self.gs.switch_side()

    def get_best_move(self, depth=2):
        moves = self.get_valid_moves()
        return random.choice(moves) if moves else None

class ChessGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Chess Game")

        self.board = [[None for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        self.squares = [[None for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        self.selected_piece = None
        self.highlighted_squares = []
        self.images = {}

        self.board_frame = tk.Frame(root, width=SQUARE_SIZE * BOARD_SIZE, height=SQUARE_SIZE * BOARD_SIZE)
        self.board_frame.pack_propagate(False)
        self.board_frame.pack(side=tk.LEFT)

        self.sidebar_frame = tk.Frame(root, width=200, bg="lightgray")
        self.sidebar_frame.pack(side=tk.RIGHT, fill=tk.Y)

        self.move_history = tk.Text(self.sidebar_frame, height=40, width=25)
        self.move_history.pack(pady=10)

        self.reset_button = tk.Button(self.sidebar_frame, text="Reset", command=self.reset_game)
        self.reset_button.pack(pady=10)

        self.load_piece_images()
        self.create_board()
        self.reset_game()

    def load_piece_images(self):
        pieces = ["b_pawn", "b_rook", "b_knight", "b_bishop", "b_queen", "b_king",
                  "w_pawn", "w_rook", "w_knight", "w_bishop", "w_queen", "w_king"]
        for piece in pieces:
            img = PhotoImage(file=f"images/{piece}.png")
            img = img.subsample(max(img.width() // SQUARE_SIZE, 1), max(img.height() // SQUARE_SIZE, 1))
            self.images[piece] = img

    def create_board(self):
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                frame = tk.Frame(self.board_frame, width=SQUARE_SIZE, height=SQUARE_SIZE)
                frame.place(x=col*SQUARE_SIZE, y=row*SQUARE_SIZE)
                label = tk.Label(frame, width=SQUARE_SIZE, height=SQUARE_SIZE)
                label.bind("<Button-1>", lambda e, r=row, c=col: self.on_square_click(r, c))
                label.pack(expand=True, fill=tk.BOTH)
                self.squares[row][col] = label

    def reset_game(self):
        self.setup_pieces()
        self.gs = GameState(self.board)
        self.engine = ChessEngine(self.gs)
        self.update_board()
        self.move_history.delete(1.0, tk.END)

    def setup_pieces(self):
        self.board = [["b_rook", "b_knight", "b_bishop", "b_queen", "b_king", "b_bishop", "b_knight", "b_rook"],
                      ["b_pawn"] * 8] + \
                     [[""] * 8 for _ in range(4)] + \
                     [["w_pawn"] * 8,
                      ["w_rook", "w_knight", "w_bishop", "w_queen", "w_king", "w_bishop", "w_knight", "w_rook"]]

    def on_square_click(self, row, col):
        piece = self.board[row][col]

        if self.selected_piece:
            if (row, col) in self.highlighted_squares:
                from_row, from_col = self.selected_piece
                self.move_piece(from_row, from_col, row, col)
                self.selected_piece = None
                self.highlighted_squares = []
                self.clear_highlights()
            else:
                self.selected_piece = None
                self.highlighted_squares = []
                self.clear_highlights()
        elif piece:
            self.selected_piece = (row, col)
            self.highlighted_squares = self.get_valid_moves(row, col)
            self.highlight_squares(self.highlighted_squares)

    def move_piece(self, from_row, from_col, to_row, to_col):
        piece = self.board[from_row][from_col]
        captured = self.board[to_row][to_col]

        if piece == "w_pawn" and to_row == 0:
            piece = "w_queen"
        elif piece == "b_pawn" and to_row == 7:
            piece = "b_queen"

        self.board[to_row][to_col] = piece
        self.board[from_row][from_col] = ""
        self.gs.switch_side()
        self.update_board()
        self.move_history.insert(tk.END, f"{piece} {from_row},{from_col} → {to_row},{to_col}\n")

    def update_board(self):
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                piece = self.board[row][col]
                label = self.squares[row][col]
                bg_color = "white" if (row + col) % 2 == 0 else "gray"
                label.config(image="", text="", bg=bg_color)
                if piece:
                    if piece in self.images:
                        label.config(image=self.images[piece])
                        label.image = self.images[piece]
                    else:
                        label.config(text=piece)

    def clear_highlights(self):
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                color = "white" if (row + col) % 2 == 0 else "gray"
                self.squares[row][col].config(bg=color)

    def highlight_squares(self, squares):
        for row, col in squares:
            self.squares[row][col].config(bg="light green")

    def get_valid_moves(self, row, col):
        moves = []
        piece = self.board[row][col]
        if not piece:
            return moves

        color = piece[0]
        kind = piece[2:]

        directions = []

        if kind == "pawn":
            direction = -1 if color == "w" else 1
            start_row = 6 if color == "w" else 1

            if self.board[row + direction][col] == "":
                moves.append((row + direction, col))
                if row == start_row and self.board[row + 2 * direction][col] == "":
                    moves.append((row + 2 * direction, col))

            for dc in [-1, 1]:
                r, c = row + direction, col + dc
                if 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE:
                    target = self.board[r][c]
                    if target and target[0] != color:
                        moves.append((r, c))

        elif kind == "knight":
            knight_moves = [(-2, -1), (-1, -2), (-2, 1), (-1, 2), (1, -2), (2, -1), (2, 1), (1, 2)]
            for dr, dc in knight_moves:
                r, c = row + dr, col + dc
                if 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE:
                    target = self.board[r][c]
                    if target == "" or target[0] != color:
                        moves.append((r, c))

        elif kind in ["rook", "bishop", "queen"]:
            if kind == "rook":
                directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
            elif kind == "bishop":
                directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
            elif kind == "queen":
                directions = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]

            for dr, dc in directions:
                r, c = row + dr, col + dc
                while 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE:
                    target = self.board[r][c]
                    if target == "":
                        moves.append((r, c))
                    elif target[0] != color:
                        moves.append((r, c))
                        break
                    else:
                        break
                    r += dr
                    c += dc

        elif kind == "king":
            for dr in [-1, 0, 1]:
                for dc in [-1, 0, 1]:
                    if dr == 0 and dc == 0:
                        continue
                    r, c = row + dr, col + dc
                    if 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE:
                        target = self.board[r][c]
                        if target == "" or target[0] != color:
                            moves.append((r, c))

        return moves

if __name__ == "__main__":
    root = tk.Tk()
    game = ChessGame(root)
    root.mainloop()
