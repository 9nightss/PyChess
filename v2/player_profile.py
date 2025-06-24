import json
import os
from collections import defaultdict

class PlayerProfile:
    def __init__(self, profile_file='player_profile.json'):
        self.profile_file = profile_file
        self.data = self.load_profile()

    def load_profile(self):
        if os.path.exists(self.profile_file):
            with open(self.profile_file, 'r') as f:
                return json.load(f)
        return {
            "openings": defaultdict(int),
            "castling_count": 0,
            "quick_queen_deploys": 0,
            "total_games": 0
        }

    def save_profile(self):
        # Convert defaultdict to regular dict for JSON serialization
        self.data["openings"] = dict(self.data["openings"])
        with open(self.profile_file, 'w') as f:
            json.dump(self.data, f, indent=2)
        # Restore as defaultdict
        self.data["openings"] = defaultdict(int, self.data["openings"])

    def update_profile(self, move_history):
        self.data["total_games"] += 1
        if move_history:
            self.data["openings"][move_history[0]] += 1

        # Track castling
        if "e1g1" in move_history or "e1c1" in move_history:
            self.data["castling_count"] += 1
        if "e8g8" in move_history or "e8c8" in move_history:
            self.data["castling_count"] += 1

        # Track fast queen deployment
        for move in move_history[:10]:
            if move[0] in ["d", "e"] and move[1] == "1" and "q" in move.lower():
                self.data["quick_queen_deploys"] += 1
                break

        self.save_profile()

    def get_opening_preferences(self):
        return sorted(self.data["openings"].items(), key=lambda x: x[1], reverse=True)

    def get_castling_rate(self):
        if self.data["total_games"] == 0:
            return 0
        return self.data["castling_count"] / self.data["total_games"]

    def get_aggression_score(self):
        if self.data["total_games"] == 0:
            return 0
        return self.data["quick_queen_deploys"] / self.data["total_games"]
