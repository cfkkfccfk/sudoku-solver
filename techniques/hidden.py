"""
hidden.py - Difficulty 4: Hidden Pair, Triple, Quad.

A Hidden Set of degree N is N values within a region that collectively
appear only in N specific cells.  All other candidates can be eliminated
from those N cells (leaving only the N hidden values).
"""
from .base import Technique, Hint
from typing import List
from itertools import combinations


class _HiddenSetBase(Technique):
    """Shared logic for Hidden Pair / Triple / Quad."""
    degree: int = 2

    def find_hints(self, grid) -> List[Hint]:
        hints = []
        seen_elims = set()

        for region in grid.all_regions:
            # For each value, collect the cells in this region where it can go
            value_places = {}
            for v in range(1, 10):
                places = frozenset(
                    (r, c) for r, c in region.cells
                    if grid.values[r][c] == 0 and v in grid.candidates[r][c]
                )
                if 2 <= len(places) <= self.degree:
                    value_places[v] = places

            if len(value_places) < self.degree:
                continue

            # Try every combination of `degree` values
            for values_combo in combinations(value_places.keys(), self.degree):
                # Union of cells that can hold any of these values
                cells_union = set()
                for v in values_combo:
                    cells_union |= value_places[v]

                if len(cells_union) != self.degree:
                    continue  # not a hidden set

                # Eliminations: other candidates in these cells
                values_set = set(values_combo)
                elims = []
                for r, c in sorted(cells_union):
                    for v in grid.candidates[r][c]:
                        if v not in values_set:
                            elims.append((r, c, v))

                if not elims:
                    continue

                elim_key = frozenset(elims)
                if elim_key in seen_elims:
                    continue
                seen_elims.add(elim_key)

                cells_str = ', '.join(f"R{r+1}C{c+1}" for r, c in sorted(cells_union))
                hints.append(Hint(
                    technique=self.name,
                    difficulty=self.difficulty,
                    description=(
                        f"{self.name}: 数值 {sorted(values_combo)} 只在 "
                        f"{region} 的 {cells_str} 中 "
                        f"→ 消去这些格的其他候选数"
                    ),
                    eliminations=elims,
                ))

        return hints


class HiddenPair(_HiddenSetBase):
    """
    Hidden Pair: 2 values in a region that only appear in the same 2 cells
    → all other candidates can be removed from those 2 cells.
    Difficulty: 4
    """
    name = "Hidden Pair"
    difficulty = 4
    degree = 2


class HiddenTriple(_HiddenSetBase):
    """
    Hidden Triple: 3 values confined to the same 3 cells in a region.
    Difficulty: 4
    """
    name = "Hidden Triple"
    difficulty = 4
    degree = 3


class HiddenQuad(_HiddenSetBase):
    """
    Hidden Quad: 4 values confined to the same 4 cells in a region.
    Difficulty: 4
    """
    name = "Hidden Quad"
    difficulty = 4
    degree = 4
