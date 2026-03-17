"""
database.py - Sudoku puzzle database backed by per-difficulty JSON files.

Files: puzzles_level1.json … puzzles_level5.json
Each file stores a list of records:
    {
        "id":         "3-10",          # "<difficulty>-<sequence>"
        "puzzle":     "530070000...",  # 81-char string
        "difficulty": 3               # 1-4: solvable; 5: needs harder techniques
    }
"""
import json
import os
import random
from typing import Optional

DB_DIR = os.path.dirname(os.path.abspath(__file__))


def _level_path(difficulty: int) -> str:
    return os.path.join(DB_DIR, f'puzzles_level{difficulty}.json')


class PuzzleDB:
    def __init__(self):
        self.data: dict = {}   # difficulty (int) -> list of records
        self._load()

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------

    def _load(self):
        # Migrate old single-file puzzles.json if it exists
        old_path = os.path.join(DB_DIR, 'puzzles.json')
        if os.path.exists(old_path):
            self._migrate(old_path)

        for d in range(1, 6):
            path = _level_path(d)
            if os.path.exists(path):
                with open(path, 'r', encoding='utf-8') as f:
                    self.data[d] = json.load(f)
            else:
                self.data[d] = []

    def _migrate(self, old_path: str):
        """Split legacy puzzles.json into per-level files, then remove it."""
        with open(old_path, 'r', encoding='utf-8') as f:
            old_puzzles = json.load(f)

        by_level: dict = {}
        for p in old_puzzles:
            by_level.setdefault(p['difficulty'], []).append(p)

        for d, puzzles in by_level.items():
            path = _level_path(d)
            if not os.path.exists(path):   # don't overwrite if already migrated
                with open(path, 'w', encoding='utf-8') as f:
                    json.dump(puzzles, f, ensure_ascii=False, indent=2)

        os.remove(old_path)

    def _save(self, difficulty: int):
        path = _level_path(difficulty)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(self.data[difficulty], f, ensure_ascii=False, indent=2)

    # ------------------------------------------------------------------
    # ID generation
    # ------------------------------------------------------------------

    def _next_id(self, difficulty: int) -> str:
        nums = [
            int(p['id'].split('-')[1])
            for p in self.data.get(difficulty, [])
            if len(p['id'].split('-')) == 2 and p['id'].split('-')[1].isdigit()
        ]
        seq = max(nums) + 1 if nums else 1
        return f"{difficulty}-{seq}"

    # ------------------------------------------------------------------
    # Write
    # ------------------------------------------------------------------

    def add(self, puzzle_str: str, difficulty: int) -> str:
        """Add a puzzle and persist. Returns the new id."""
        if difficulty not in self.data:
            self.data[difficulty] = []
        puzzle_id = self._next_id(difficulty)
        self.data[difficulty].append({
            'id':         puzzle_id,
            'puzzle':     puzzle_str,
            'difficulty': difficulty,
        })
        self._save(difficulty)
        return puzzle_id

    # ------------------------------------------------------------------
    # Query
    # ------------------------------------------------------------------

    def exists(self, puzzle_str: str) -> bool:
        return any(
            p['puzzle'] == puzzle_str
            for puzzles in self.data.values()
            for p in puzzles
        )

    def get_by_difficulty(self, difficulty: int) -> list:
        return list(self.data.get(difficulty, []))

    def get_by_index(self, difficulty: int, index: int) -> Optional[dict]:
        """1-based index within the difficulty group. Returns None if out of range."""
        group = self.get_by_difficulty(difficulty)
        if 1 <= index <= len(group):
            return group[index - 1]
        return None

    def get_random(self, difficulty: int) -> Optional[dict]:
        group = self.get_by_difficulty(difficulty)
        return random.choice(group) if group else None

    def all_difficulties(self) -> list:
        """Return sorted list of difficulty levels that have at least one puzzle."""
        return sorted(d for d, puzzles in self.data.items() if puzzles)

    def count(self, difficulty: int = None) -> int:
        if difficulty is None:
            return sum(len(v) for v in self.data.values())
        return len(self.data.get(difficulty, []))

    # ------------------------------------------------------------------
    # Display
    # ------------------------------------------------------------------

    def summary(self) -> str:
        if self.count() == 0:
            return "数据库为空"
        parts = [f"难度{d}×{self.count(d)}" for d in self.all_difficulties()]
        return f"共 {self.count()} 题  ({', '.join(parts)})"
