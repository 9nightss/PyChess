import tkinter as tk
from tkinter import simpledialog
from PIL import Image, ImageTk
import random
import ctypes
import json
import time
from collections import defaultdict
from datetime import datetime, timedelta

class LearningModule:
    def __init__(self, cache_file="learning_cache.json"):
        self.cache_file = cache_file
        self.history = defaultdict(list)
        self.load_cache()

    def load_cache(self):
        try:
            with open(self.cache_file, "r") as f:
                raw = json.load(f)
                for fen, records in raw.items():
                    self.history[fen] = records
        except FileNotFoundError:
            self.history = defaultdict(list)

    def save_cache(self):
        with open(self.cache_file, "w") as f:
            json.dump(self.history, f, indent=2)

    def record_result(self, fen, move, outcome):
        self.history[fen].append({
            "move": move,
            "outcome": outcome,
            "timestamp": time.time()
        })

    def cleanup_old_data(self, weeks=3):
        cutoff = time.time() - (weeks * 7 * 24 * 3600)
        for fen in list(self.history.keys()):
            self.history[fen] = [r for r in self.history[fen] if r["timestamp"] > cutoff]
            if not self.history[fen]:
                del self.history[fen]

    def choose_best_move(self, fen):
        records = self.history.get(fen, [])
        if not records:
            return None
        move_stats = defaultdict(lambda: {"score": 0, "count": 0})
        for rec in records:
            move = tuple(rec["move"])
            move_stats[move]["score"] += rec["outcome"]
            move_stats[move]["count"] += 1
        scored = [(move, data["score"] / data["count"]) for move, data in move_stats.items()]
        scored.sort(key=lambda x: x[1], reverse=True)
        return scored[0][0] if scored else None

class ChessGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Chess Game")
        self.board = [[None for _ in range(8)] for _ in range(8)]
        self.images = {}
        self.selected_piece = None
        self.valid_moves = []
        self.turn = "white"
        self.canvas = tk.Canvas(root, width=640, height=640)
        self.canvas.pack()
        self.canvas.bind("<Button-1>", self.on_click)
        self.history = []
        self.white_king_moved = False
        self.black_king_moved = False
        self.white_rook_moved = [False, False]
        self.black_rook_moved = [False, False]
        self.en_passant_target = None
        self.learner = LearningModule()
        self.load_images()
        self.setup_board()
        self.draw_board()

    def load_images(self):
        pieces = ["king", "queen", "rook", "bishop", "knight", "pawn"]
        colors = ["w", "b"]
        for color in colors:
            for piece in pieces:
                image = Image.open(f"images/{color}_{piece}.png")
                image = image.resize((80, 80), Image.LANCZOS)
                self.images[f"{color}_{piece}"] = ImageTk.PhotoImage(image)

    def setup_board(self):
        self.board[0] = ["b_rook", "b_knight", "b_bishop", "b_queen", "b_king", "b_bishop", "b_knight", "b_rook"]
        self.board[1] = ["b_pawn"] * 8
        self.board[6] = ["w_pawn"] * 8
        self.board[7] = ["w_rook", "w_knight", "w_bishop", "w_queen", "w_king", "w_bishop", "w_knight", "w_rook"]

    def draw_board(self):
        colors = ["#D18B47", "#FFCE9E"]
        self.canvas.delete("all")
        for row in range(8):
            for col in range(8):
                color = colors[(row + col) % 2]
                x1, y1 = col * 80, row * 80
                x2, y2 = x1 + 80, y1 + 80
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline=color)
                if (row, col) in self.valid_moves:
                    self.canvas.create_oval(x1+30, y1+30, x2-30, y2-30, fill="#888", outline="")
                piece = self.board[row][col]
                if piece:
                    self.canvas.create_image(x1, y1, image=self.images[piece], anchor="nw")

    def on_click(self, event):
        col = event.x // 80
        row = event.y // 80
        if self.selected_piece:
            start_row, start_col = self.selected_piece
            if (row, col) in self.valid_moves:
                self.make_move(start_row, start_col, row, col)
                self.selected_piece = None
                self.valid_moves = []
                self.draw_board()
                if self.check_game_end():
                    return
                self.turn = "black" if self.turn == "white" else "white"
                if self.turn == "black":
                    self.root.after(500, self.ai_move)
            else:
                self.selected_piece = (row, col) if self.is_current_turn_piece(row, col) else None
                self.valid_moves = self.get_valid_moves(row, col) if self.selected_piece else []
                self.draw_board()
        else:
            if self.is_current_turn_piece(row, col):
                self.selected_piece = (row, col)
                self.valid_moves = self.get_valid_moves(row, col)
                self.draw_board()

    def is_current_turn_piece(self, row, col):
        piece = self.board[row][col]
        return piece and piece[0] == self.turn[0]

    def make_move(self, sr, sc, er, ec):
        piece = self.board[sr][sc]
        target = self.board[er][ec]
        self.history.append((sr, sc, er, ec, target))
        self.board[er][ec] = piece
        self.board[sr][sc] = None
        if piece.endswith("pawn") and abs(er - sr) == 2:
            self.en_passant_target = ((sr + er) // 2, sc)
        else:
            self.en_passant_target = None
        if piece == "w_king": self.white_king_moved = True
        if piece == "b_king": self.black_king_moved = True
        if piece == "w_rook":
            if sc == 0: self.white_rook_moved[0] = True
            if sc == 7: self.white_rook_moved[1] = True
        if piece == "b_rook":
            if sc == 0: self.black_rook_moved[0] = True
            if sc == 7: self.black_rook_moved[1] = True
        if piece.endswith("pawn") and (er == 0 or er == 7):
            self.promote_pawn(er, ec)

    def promote_pawn(self, row, col):
        choice = simpledialog.askstring("Promotion", "Promote to (queen/rook/bishop/knight):", parent=self.root)
        if choice in ["queen", "rook", "bishop", "knight"]:
            color = self.board[row][col][0]
            self.board[row][col] = f"{color}_{choice}"

    def ai_move(self):
        all_moves = [(r, c, er, ec)
                     for r in range(8) for c in range(8)
                     if self.is_current_turn_piece(r, c)
                     for (er, ec) in self.get_valid_moves(r, c)]
        fen = self.board_to_fen()
        best = self.learner.choose_best_move(fen)
        if best:
            sr, sc, er, ec = best
        elif all_moves:
            sr, sc, er, ec = random.choice(all_moves)
        else:
            return
        self.make_move(sr, sc, er, ec)
        self.learner.record_result(fen, (sr, sc, er, ec), +1)
        self.learner.save_cache()
        self.draw_board()
        if self.check_game_end():
            return
        self.turn = "white"

    def board_to_fen(self):
        fen = ""
        for row in self.board:
            empty = 0
            for piece in row:
                if not piece:
                    empty += 1
                else:
                    if empty:
                        fen += str(empty)
                        empty = 0
                    sym = piece.split("_")[1][0]
                    fen += sym.upper() if piece.startswith("w") else sym
            if empty:
                fen += str(empty)
            fen += "/"
        fen = fen[:-1] + f" {self.turn[0]}"
        return fen

    def get_valid_moves(self, row, col):
        piece = self.board[row][col]
        if not piece: return []
        directions = {
            "pawn": [(-1, 0), (-2, 0), (-1, -1), (-1, 1)] if piece.startswith("w") else [(1, 0), (2, 0), (1, -1), (1, 1)],
            "rook": [(0, 1), (1, 0), (0, -1), (-1, 0)],
            "bishop": [(1, 1), (1, -1), (-1, 1), (-1, -1)],
            "queen": [(0, 1), (1, 0), (0, -1), (-1, 0), (1, 1), (1, -1), (-1, 1), (-1, -1)],
            "king": [(0, 1), (1, 0), (0, -1), (-1, 0), (1, 1), (1, -1), (-1, 1), (-1, -1)],
            "knight": [(2, 1), (1, 2), (-1, 2), (-2, 1), (-2, -1), (-1, -2), (1, -2), (2, -1)]
        }
        kind = piece.split("_")[1]
        color = piece[0]
        moves = []

        for dr, dc in directions.get(kind, []):
            for i in range(1, 2 if kind in ["king", "knight", "pawn"] else 8):
                nr, nc = row + dr * i, col + dc * i
                if not (0 <= nr < 8 and 0 <= nc < 8):
                    break
                target = self.board[nr][nc]
                if kind == "pawn":
                    if dc == 0:
                        if not target:
                            moves.append((nr, nc))
                            if abs(dr) == 2 and ((color == "w" and row == 6) or (color == "b" and row == 1)):
                                continue
                        else:
                            break
                    elif abs(dc) == 1:
                        if target and target[0] != color:
                            moves.append((nr, nc))
                        elif (nr, nc) == self.en_passant_target:
                            moves.append((nr, nc))
                    break
                elif kind in ["knight", "king"]:
                    if not target or target[0] != color:
                        moves.append((nr, nc))
                    break
                else:
                    if not target:
                        moves.append((nr, nc))
                    elif target[0] != color:
                        moves.append((nr, nc))
                        break
                    else:
                        break
        return moves

    def check_game_end(self):
        king_present = {"w": False, "b": False}
        for row in self.board:
            for piece in row:
                if piece == "w_king":
                    king_present["w"] = True
                elif piece == "b_king":
                    king_present["b"] = True
        if not king_present["w"]:
            return not self.ask_restart("Checkmate! Black wins. Play again?")
        elif not king_present["b"]:
            return not self.ask_restart("Checkmate! White wins. Play again?")
        return False

    def ask_restart(self, message):
        return ctypes.windll.user32.MessageBoxW(0, message, "Game Over", 1) == 1

if __name__ == "__main__":
    root = tk.Tk()
    game = ChessGame(root)
    root.mainloop()
