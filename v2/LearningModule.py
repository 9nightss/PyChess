import json
import time
from collections import defaultdict
from datetime import datetime, timedelta
from chess_engine import ChessEngine
class LearningModule:
    def __init__(self, cache_file="learning_cache.json"):
        self.cache_file = cache_file
        self.history = defaultdict(list)  # board_state_fen: [ {move, outcome, timestamp}, ... ]
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
            "outcome": outcome,  # +1 = win, 0 = draw, -1 = loss
            "timestamp": time.time()
        })

    def cleanup_old_data(self, weeks=3):
        cutoff = time.time() - (weeks * 7 * 24 * 3600)
        for fen in list(self.history.keys()):
            self.history[fen] = [r for r in self.history[fen] if r["timestamp"] > cutoff]
            if not self.history[fen]:
                del self.history[fen]
