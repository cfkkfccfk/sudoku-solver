"""
single.py - Difficulty 1: NakedSingle and HiddenSingle.

NakedSingle  : A cell has only one candidate left → fill it.
HiddenSingle : A value can go in only one cell in a region → fill it.
"""
from .base import Technique, Hint
from typing import List


class NakedSingle(Technique):
    """
    Naked Single: a cell has exactly 1 candidate remaining.
    The cell must be set to that value.
    Difficulty: 1
    """
    name = "Naked Single"
    difficulty = 1

    def find_hints(self, grid) -> List[Hint]:
        hints = []
        for r in range(9):
            for c in range(9):
                if grid.values[r][c] == 0 and len(grid.candidates[r][c]) == 1:
                    value = next(iter(grid.candidates[r][c]))
                    hints.append(Hint(
                        technique=self.name,
                        difficulty=self.difficulty,
                        description=(
                            f"R{r+1}C{c+1} = {value}  "
                            f"(唯一候选数)"
                        ),
                        cell_value=(r, c, value),
                    ))
        return hints


class HiddenSingle(Technique):
    """
    Hidden Single: a value can be placed in only one cell within a region
    (row, column, or box).  That cell must be set to that value.
    Difficulty: 1
    """
    name = "Hidden Single"
    difficulty = 1

    def find_hints(self, grid) -> List[Hint]:
        hints = []
        seen = set()  # avoid duplicates when same cell/value found in multiple regions

        for region in grid.all_regions:
            for v in range(1, 10):
                # Cells in this region where v is still a candidate
                places = [
                    (r, c) for r, c in region.cells
                    if grid.values[r][c] == 0 and v in grid.candidates[r][c]
                ]
                if len(places) == 1:
                    r, c = places[0]
                    key = (r, c, v)
                    if key not in seen:
                        seen.add(key)
                        hints.append(Hint(
                            technique=self.name,
                            difficulty=self.difficulty,
                            description=(
                                f"R{r+1}C{c+1} = {v}  "
                                f"({region.type} {region.index} 中唯一能填 {v} 的格)"
                            ),
                            cell_value=(r, c, v),
                        ))
        return hints
