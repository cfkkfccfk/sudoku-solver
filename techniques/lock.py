"""
lock.py - Difficulty 2: Pointing and Claiming (Box-Line Reduction).

Pointing : All candidates for value V in a box lie in the same row/col
           → V can be eliminated from the rest of that row/col.
Claiming : All candidates for value V in a row/col lie in the same box
           → V can be eliminated from the rest of that box.
"""
from .base import Technique, Hint
from typing import List


class Locking(Technique):
    """
    Locking (Pointing + Claiming):
    When all occurrences of a candidate in one region are also confined
    to a second intersecting region, that candidate can be eliminated
    from the rest of the second region.
    Difficulty: 2
    """
    name = "Locking"
    difficulty = 2

    def find_hints(self, grid) -> List[Hint]:
        hints = []

        # --- Pointing: box → row or col ---
        for box in grid.boxes:
            for v in range(1, 10):
                places = [
                    (r, c) for r, c in box.cells
                    if grid.values[r][c] == 0 and v in grid.candidates[r][c]
                ]
                if not places:
                    continue

                rows_used = {r for r, c in places}
                cols_used = {c for r, c in places}

                # All candidates in this box are in the same row
                if len(rows_used) == 1:
                    row = next(iter(rows_used))
                    bc = box.cells[0][1] // 3  # box column index 0-2
                    elims = [
                        (row, c, v)
                        for r2, c in grid.rows[row].cells
                        if c // 3 != bc
                        and grid.values[row][c] == 0
                        and v in grid.candidates[row][c]
                    ]
                    if elims:
                        hints.append(Hint(
                            technique="Pointing",
                            difficulty=self.difficulty,
                            description=(
                                f"Pointing: {v} 在 {box} 中只在 row {row+1} → "
                                f"消去 row {row+1} 其余格中的 {v}"
                            ),
                            eliminations=elims,
                        ))

                # All candidates in this box are in the same column
                if len(cols_used) == 1:
                    col = next(iter(cols_used))
                    br = box.cells[0][0] // 3  # box row index 0-2
                    elims = [
                        (r, col, v)
                        for r, c2 in grid.cols[col].cells
                        if r // 3 != br
                        and grid.values[r][col] == 0
                        and v in grid.candidates[r][col]
                    ]
                    if elims:
                        hints.append(Hint(
                            technique="Pointing",
                            difficulty=self.difficulty,
                            description=(
                                f"Pointing: {v} 在 {box} 中只在 col {col+1} → "
                                f"消去 col {col+1} 其余格中的 {v}"
                            ),
                            eliminations=elims,
                        ))

        # --- Claiming: row → box ---
        for row_region in grid.rows:
            r = row_region.index - 1
            for v in range(1, 10):
                places = [
                    (r2, c) for r2, c in row_region.cells
                    if grid.values[r2][c] == 0 and v in grid.candidates[r2][c]
                ]
                if not places:
                    continue
                boxes_used = {c // 3 for _, c in places}
                if len(boxes_used) == 1:
                    bc = next(iter(boxes_used))
                    br = r // 3
                    box = grid.boxes[br * 3 + bc]
                    elims = [
                        (r2, c, v)
                        for r2, c in box.cells
                        if r2 != r
                        and grid.values[r2][c] == 0
                        and v in grid.candidates[r2][c]
                    ]
                    if elims:
                        hints.append(Hint(
                            technique="Claiming",
                            difficulty=self.difficulty,
                            description=(
                                f"Claiming: {v} 在 row {r+1} 中只在 {box} → "
                                f"消去 {box} 其余格中的 {v}"
                            ),
                            eliminations=elims,
                        ))

        # --- Claiming: col → box ---
        for col_region in grid.cols:
            c = col_region.index - 1
            for v in range(1, 10):
                places = [
                    (r, c2) for r, c2 in col_region.cells
                    if grid.values[r][c2] == 0 and v in grid.candidates[r][c2]
                ]
                if not places:
                    continue
                boxes_used = {r // 3 for r, _ in places}
                if len(boxes_used) == 1:
                    br = next(iter(boxes_used))
                    bc = c // 3
                    box = grid.boxes[br * 3 + bc]
                    elims = [
                        (r, c2, v)
                        for r, c2 in box.cells
                        if c2 != c
                        and grid.values[r][c2] == 0
                        and v in grid.candidates[r][c2]
                    ]
                    if elims:
                        hints.append(Hint(
                            technique="Claiming",
                            difficulty=self.difficulty,
                            description=(
                                f"Claiming: {v} 在 col {c+1} 中只在 {box} → "
                                f"消去 {box} 其余格中的 {v}"
                            ),
                            eliminations=elims,
                        ))

        return hints
