"""
naked.py - Difficulty 3: Naked Pair, Triple, Quad.

A Naked Set of degree N is N cells within a region whose combined
candidates contain exactly N values.  Those N values are "locked into"
these N cells, so they can be eliminated from all other cells in every
region shared by those N cells.
"""
from .base import Technique, Hint
from typing import List
from itertools import combinations


class _NakedSetBase(Technique):
    """Shared logic for Naked Pair / Triple / Quad."""
    degree: int = 2

    def find_hints(self, grid) -> List[Hint]:
        hints = []
        seen_elims = set()  # deduplicate identical elimination sets

        for region in grid.all_regions:
            # Candidate cells: empty, with 2..degree candidates
            candidates_cells = [
                (r, c) for r, c in region.cells
                if grid.values[r][c] == 0
                and 2 <= len(grid.candidates[r][c]) <= self.degree
            ]

            # Try every combination of `degree` cells
            for combo in combinations(candidates_cells, self.degree):
                union = set()
                for r, c in combo:
                    union |= grid.candidates[r][c]

                if len(union) != self.degree:
                    continue  # not a naked set

                # Find eliminations: other cells in this region that hold any
                # of these values
                elims = []
                for r, c in region.cells:
                    if (r, c) in combo:
                        continue
                    if grid.values[r][c] != 0:
                        continue
                    for v in union:
                        if v in grid.candidates[r][c]:
                            elims.append((r, c, v))

                if not elims:
                    continue

                # Deduplicate by frozen eliminations set
                elim_key = frozenset(elims)
                if elim_key in seen_elims:
                    continue
                seen_elims.add(elim_key)

                cells_str = ', '.join(f"R{r+1}C{c+1}" for r, c in combo)
                hints.append(Hint(
                    technique=self.name,
                    difficulty=self.difficulty,
                    description=(
                        f"{self.name}: {cells_str} 共享候选数 {sorted(union)} "
                        f"→ 从 {region} 其余格消去这些数"
                    ),
                    eliminations=elims,
                ))

        return hints


class NakedPair(_NakedSetBase):
    """
    Naked Pair: 2 cells in a region whose combined candidates are exactly
    2 values → eliminate both values from all other cells in that region.
    Difficulty: 3
    """
    name = "Naked Pair"
    difficulty = 3
    degree = 2


class NakedTriple(_NakedSetBase):
    """
    Naked Triple: 3 cells sharing exactly 3 candidate values.
    Each cell may have 2 or 3 of these values.
    Difficulty: 3
    """
    name = "Naked Triple"
    difficulty = 3
    degree = 3


class NakedQuad(_NakedSetBase):
    """
    Naked Quad: 4 cells sharing exactly 4 candidate values.
    Difficulty: 3
    """
    name = "Naked Quad"
    difficulty = 3
    degree = 4
