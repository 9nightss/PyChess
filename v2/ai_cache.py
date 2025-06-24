import tkinter as tk
from tkinter import simpledialog
from PIL import Image, ImageTk
import random
import ctypes
import json
import time
import winsound
from collections import defaultdict
from datetime import datetime

# === Learning & Caching Module ===
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

# === AI Cache for Board Pattern Learning ===
class AICache:
    def __init__(self, file="ai_board_cache.json"):
        self.file = file
        self.data = defaultdict(list)
        self.load()

    def load(self):
        try:
            with open(self.file, "r") as f:
                self.data = json.load(f)
        except FileNotFoundError:
            self.data = defaultdict(list)

    def save(self):
        with open(self.file, "w") as f:
            json.dump(self.data, f, indent=2)

    def record(self, fen, move):
        self.data.setdefault(fen, []).append({"move": move, "ts": time.time()})

# === Player Behavior Tracker ===
class PlayerProfile:
    def __init__(self, file="player_profile.json"):
        self.file = file
        self.profile = {
            "early_queen_moves": 0,
            "castle_moves": 0,
            "games_played": 0,
            "timestamp": str(datetime.now())
        }
        self.load()

    def load(self):
        try:
            with open(self.file, "r") as f:
                self.profile.update(json.load(f))
        except FileNotFoundError:
            pass

    def save(self):
        with open(self.file, "w") as f:
            json.dump(self.profile, f, indent=2)

    def track_move(self, piece, move_num, move_type=None):
        if move_num < 10 and "queen" in piece:
            self.profile["early_queen_moves"] += 1
        if move_type == "castle":
            self.profile["castle_moves"] += 1

    def end_game(self):
        self.profile["games_played"] += 1
        self.profile["timestamp"] = str(datetime.now())
        self.save()

# === Main Chess Game ===
class ChessGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Chess Game")
        self.canvas = tk.Canvas(root, width=640, height=640)
        self.canvas.pack()
        self.canvas.bind("<Button-1>", self.on_click)

        self.board = [[None for _ in range(8)] for _ in range(8)]
        self.images = {}
        self.selected_piece = None
        self.valid_moves = []
        self.turn = "white"
        self.history = []
        self.en_passant_target = None
        self.move_count = 0

        self.white_king_moved = False
        self.black_king_moved = False
        self.white_rook_moved = [False, False]
        self.black_rook_moved = [False, False]

        self.learner = LearningModule()
        self.cache = AICache()
        self.profile = PlayerProfile()

        self.load_images()
        self.setup_board()
        self.draw_board()

    def load_images(self):
        pieces = ["king", "queen", "rook", "bishop", "knight", "pawn"]
        colors = ["w", "b"]
        for color in colors:
            for piece in pieces:
                img = Image.open(f"images/{color}_{piece}.png").resize((80, 80), Image.LANCZOS)
                self.images[f"{color}_{piece}"] = ImageTk.PhotoImage(img)

    def setup_board(self):
        self.board[0] = ["b_rook", "b_knight", "b_bishop", "b_queen", "b_king", "b_bishop", "b_knight", "b_rook"]
        self.board[1] = ["b_pawn"] * 8
        self.board[6] = ["w_pawn"] * 8
        self.board[7] = ["w_rook", "w_knight", "w_bishop", "w_queen", "w_king", "w_bishop", "w_knight", "w_rook"]

    def draw_board(self):
        # === Board Themes: Uncomment the one you want ===
        # colors = ["#D18B47", "#FFCE9E"]  # Classic wood
        # colors = ["#769656", "#EEEED2"]  # Lichess green
        # colors = ["#B58863", "#F0D9B5"]  # Chess.com style
        colors = ["#444444", "#EEEEEE"]  # Minimalist frosted black/white glass theme

        # colors = ["#333", "#DDD"]  # High contrast

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
        col, row = event.x // 80, event.y // 80
        if self.selected_piece:
            sr, sc = self.selected_piece
            if (row, col) in self.valid_moves:
                self.make_move(sr, sc, row, col)
                self.selected_piece = None
                self.valid_moves = []
                self.draw_board()
                if self.check_game_end(): return
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
        self.move_count += 1
        self.board[er][ec] = piece
        self.board[sr][sc] = None
        self.play_move_sound()
        self.history.append((sr, sc, er, ec))
        if piece.endswith("pawn") and abs(er - sr) == 2:
            self.en_passant_target = ((sr + er) // 2, sc)
        else:
            self.en_passant_target = None

        if piece == "w_king": self.white_king_moved = True
        if piece == "b_king": self.black_king_moved = True
        if piece == "w_rook": self.white_rook_moved[0 if sc == 0 else 1] = True
        if piece == "b_rook": self.black_rook_moved[0 if sc == 0 else 1] = True

        if piece.endswith("pawn") and (er == 0 or er == 7):
            self.promote_pawn(er, ec)

    import winsound

    def play_move_sound(self):
        try:
            winsound.PlaySound(
                r"C:\Users\ab_fa\OneDrive\Documents\My-Projects\busy coding\chess_ai\v2\images\move-self.wav",
                winsound.SND_FILENAME | winsound.SND_ASYNC
            )
        except Exception as e:
            print("Sound error:", e)
    
            
    def promote_pawn(self, row, col):
        choice = simpledialog.askstring("Promotion", "Promote to (queen/rook/bishop/knight):", parent=self.root)
        if choice in ["queen", "rook", "bishop", "knight"]:
            color = self.board[row][col][0]
            self.board[row][col] = f"{color}_{choice}"
    def is_in_check(self, color):
        king_pos = None
        for r in range(8):
            for c in range(8):
                if self.board[r][c] == f"{color}_king":
                    king_pos = (r, c)
                    break
            if king_pos:
                break
        if not king_pos:
            return True  # king is missing, technically in checkmate
        opponent_color = "b" if color == "w" else "w"
        for r in range(8):
            for c in range(8):
                if self.board[r][c] and self.board[r][c][0] == opponent_color:
                    if king_pos in self.get_valid_moves(r, c):
                        return True
        return False

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
        self.cache.record(fen, (sr, sc, er, ec))
        self.learner.save_cache()
        self.cache.save()
        self.draw_board()
        if self.check_game_end(): return
        self.turn = "white"
        if self.is_in_check("w"):
            print("White is in check!")
        if self.is_in_check("b"):
            print("Black is in check!")
    def ai_move(self):
        all_moves = [(r, c, er, ec)
                    for r in range(8) for c in range(8)
                    if self.is_current_turn_piece(r, c)
                    for (er, ec) in self.get_valid_moves(r, c)]
        
        # Get current FEN
        fen = self.board_to_fen()

        # Check if queen is under threat
        queen_pos = None
        for r in range(8):
            for c in range(8):
                if self.board[r][c] == "b_queen":
                    queen_pos = (r, c)
                    break
            if queen_pos:
                break

        # Check if queen is under attack
        if queen_pos and self.is_square_threatened(queen_pos[0], queen_pos[1], "w"):
            for move in all_moves:
                # Simulate move
                sr, sc, er, ec = move
                piece = self.board[sr][sc]
                backup = self.board[er][ec]
                self.board[er][ec] = piece
                self.board[sr][sc] = None
                safe = not self.is_square_threatened(er, ec, "w") if piece == "b_queen" else True
                self.board[sr][sc] = piece
                self.board[er][ec] = backup
                if safe:
                    self.make_move(sr, sc, er, ec)
                    self.learner.record_result(fen, (sr, sc, er, ec), +1)
                    self.learner.save_cache()
                    self.draw_board()
                    self.turn = "white"
                    return

        # Otherwise fallback to best learned or random
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
        self.turn = "white"

    def is_square_threatened(self, row, col, by_color):
        for r in range(8):
            for c in range(8):
                piece = self.board[r][c]
                if piece and piece[0] == by_color:
                    if (row, col) in self.get_valid_moves(r, c):
                        return True
        return False

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
        return fen[:-1] + f" {self.turn[0]}"
    def get_valid_moves(self, r, c):
        piece = self.board[r][c]
        if piece == "--":
            return []

        color, kind = piece[0], piece[1]
        moves = []
        directions = {
            'P': [(-1, 0), (-1, -1), (-1, 1)] if color == 'w' else [(1, 0), (1, -1), (1, 1)],
            'N': [(-2, -1), (-2, 1), (-1, -2), (-1, 2),
                (1, -2), (1, 2), (2, -1), (2, 1)],
            'B': [(-1, -1), (-1, 1), (1, -1), (1, 1)],
            'R': [(-1, 0), (1, 0), (0, -1), (0, 1)],
            'Q': [(-1, -1), (-1, 1), (1, -1), (1, 1),
                (-1, 0), (1, 0), (0, -1), (0, 1)],
            'K': [(-1, -1), (-1, 0), (-1, 1),
                (0, -1),          (0, 1),
                (1, -1), (1, 0), (1, 1)]
        }

        def in_bounds(row, col):
            return 0 <= row < 8 and 0 <= col < 8

        def is_enemy(row, col):
            return self.board[row][col] != "--" and self.board[row][col][0] != color

        if kind == "P":
            direction = -1 if color == "w" else 1
            start_row = 6 if color == "w" else 1
            # Forward move
            if in_bounds(r + direction, c) and self.board[r + direction][c] == "--":
                moves.append((r + direction, c))
                if r == start_row and self.board[r + 2 * direction][c] == "--":
                    moves.append((r + 2 * direction, c))
            # Captures
            for dr, dc in directions['P'][1:]:
                nr, nc = r + dr, c + dc
                if in_bounds(nr, nc) and is_enemy(nr, nc):
                    moves.append((nr, nc))
            # En passant
            if self.en_passant_square:
                ep_r, ep_c = self.en_passant_square
                if r == (3 if color == 'w' else 4) and abs(ep_c - c) == 1 and ep_r == r + direction:
                    moves.append((ep_r, ep_c))

        elif kind in ["N", "K"]:
            for dr, dc in directions[kind]:
                nr, nc = r + dr, c + dc
                if in_bounds(nr, nc):
                    target = self.board[nr][nc]
                    if target == "--" or target[0] != color:
                        moves.append((nr, nc))

            # Castling
            if kind == "K" and not self.is_in_check(color):
                row = 7 if color == "w" else 0
                if self.castling_rights[color]["kingside"]:
                    if self.board[row][5] == "--" and self.board[row][6] == "--":
                        if not self.square_under_attack(row, 5, color) and not self.square_under_attack(row, 6, color):
                            moves.append((row, 6))  # Kingside castle
                if self.castling_rights[color]["queenside"]:
                    if self.board[row][3] == "--" and self.board[row][2] == "--" and self.board[row][1] == "--":
                        if not self.square_under_attack(row, 3, color) and not self.square_under_attack(row, 2, color):
                            moves.append((row, 2))  # Queenside castle

        elif kind in ["B", "R", "Q"]:
            for dr, dc in directions[kind]:
                for i in range(1, 8):
                    nr, nc = r + dr * i, c + dc * i
                    if in_bounds(nr, nc):
                        target = self.board[nr][nc]
                        if target == "--":
                            moves.append((nr, nc))
                        elif target[0] != color:
                            moves.append((nr, nc))
                            break
                        else:
                            break
                    else:
                        break

        # Filter out illegal moves (e.g. moves leaving king in check)
        legal_moves = []
        for move in moves:
            backup_board = [row[:] for row in self.board]
            backup_en_passant = self.en_passant_square
            backup_castling = {side: self.castling_rights[side].copy() for side in self.castling_rights}

            captured = self.board[move[0]][move[1]]
            self.make_move((r, c), move)
            if not self.is_in_check(color):
                legal_moves.append(move)

            self.board = backup_board
            self.en_passant_square = backup_en_passant
            self.castling_rights = backup_castling

        return legal_moves


    def check_game_end(self):
        king_present = {"w": False, "b": False}
        for row in self.board:
            for piece in row:
                if piece == "w_king":
                    king_present["w"] = True
                elif piece == "b_king":
                    king_present["b"] = True

        if not king_present["w"]:
            self.profile.end_game()
            tk.messagebox.showinfo("Game Over", "Black wins!")
            return True
        elif not king_present["b"]:
            self.profile.end_game()
            tk.messagebox.showinfo("Game Over", "White wins!")
            return True
        return False

    def ask_restart(self, message):
        return ctypes.windll.user32.MessageBoxW(0, message, "Game Over", 1) == 1

if __name__ == "__main__":
    root = tk.Tk()
    game = ChessGame(root)
    root.mainloop()
