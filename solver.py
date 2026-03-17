"""
solver.py - Main Sudoku solver orchestrating all techniques.

To add a new technique later:
    1. Implement it as a subclass of Technique in techniques/
    2. Add an instance to DEFAULT_TECHNIQUES (in difficulty order)
"""
from grid import Grid
from techniques.base import Hint, Technique
from techniques.single import NakedSingle, HiddenSingle
from techniques.lock import Locking
from techniques.naked import NakedPair, NakedTriple, NakedQuad
from techniques.hidden import HiddenPair, HiddenTriple, HiddenQuad
from typing import List, Optional


# -----------------------------------------------------------------------
# Registered techniques in difficulty order (easiest first).
# Add harder techniques here to extend the solver.
# -----------------------------------------------------------------------
DEFAULT_TECHNIQUES: List[Technique] = [
    NakedSingle(),    # difficulty 1
    HiddenSingle(),   # difficulty 1
    Locking(),        # difficulty 2  (Pointing + Claiming)
    NakedPair(),      # difficulty 3
    NakedTriple(),    # difficulty 3
    NakedQuad(),      # difficulty 3
    HiddenPair(),     # difficulty 4
    HiddenTriple(),   # difficulty 4
    HiddenQuad(),     # difficulty 4
    # --- Add harder techniques below this line ---
    # e.g. XWing(), Swordfish(), XYWing(), Chaining(), ...
]

DIFFICULTY_NAMES = {
    1: "基础单数 (Single)",
    2: "锁定 (Locking)",
    3: "裸数组 (Naked Set)",
    4: "隐性数组 (Hidden Set)",
}


class SolveStep:
    """Records one step of the solving process."""

    def __init__(self, step_num: int, hint: Hint,
                 grid_before: Grid, grid_after: Grid):
        self.step_num = step_num
        self.hint = hint
        self.grid_before = grid_before
        self.grid_after = grid_after

    def __repr__(self):
        return f"Step {self.step_num}: {self.hint.summary()}"


class Solver:
    """
    Orchestrates all registered solving techniques.
    Techniques are tried in order; the first applicable hint is used.
    """

    def __init__(self, techniques: List[Technique] = None):
        self.techniques = techniques if techniques is not None else DEFAULT_TECHNIQUES

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _apply_hint(self, grid: Grid, hint: Hint) -> Grid:
        """Apply a hint to a copy of the grid and return the new grid."""
        new_grid = grid.copy()
        if hint.cell_value:
            r, c, v = hint.cell_value
            new_grid.set_value(r, c, v)
        for r, c, v in hint.eliminations:
            new_grid.eliminate(r, c, v)
        return new_grid

    def _find_next_hint(self, grid: Grid) -> Optional[Hint]:
        """Return the first hint from the easiest applicable technique."""
        for technique in self.techniques:
            hint = technique.find_first_hint(grid)
            if hint:
                return hint
        return None

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def analyze_difficulty(self, grid: Grid) -> int:
        """
        Solve the puzzle and return the maximum difficulty level required.
        Returns -1 if the puzzle cannot be solved with available techniques.
        """
        current = grid.copy()
        max_difficulty = 0

        while not current.is_solved():
            hint = self._find_next_hint(current)
            if hint is None:
                return -1  # stuck — needs harder techniques
            max_difficulty = max(max_difficulty, hint.difficulty)
            current = self._apply_hint(current, hint)

        return max_difficulty

    def solve(self, grid: Grid) -> Optional[Grid]:
        """
        Solve the puzzle completely.
        Returns the solved Grid, or None if unsolvable with current techniques.
        """
        current = grid.copy()

        while not current.is_solved():
            hint = self._find_next_hint(current)
            if hint is None:
                return None
            current = self._apply_hint(current, hint)

        return current

    def generate_steps(self, grid: Grid) -> List[SolveStep]:
        """
        Generate the full step-by-step solution.
        Returns as many steps as possible (may not reach completion if
        the puzzle requires techniques beyond what is registered).
        """
        steps: List[SolveStep] = []
        current = grid.copy()
        step_num = 1

        while not current.is_solved():
            hint = self._find_next_hint(current)
            if hint is None:
                break
            new_grid = self._apply_hint(current, hint)
            steps.append(SolveStep(step_num, hint, current, new_grid))
            current = new_grid
            step_num += 1

        return steps
