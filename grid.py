"""
grid.py - Sudoku grid data structure with candidate tracking.
"""
from copy import deepcopy
from itertools import product as iproduct
from typing import List, Tuple, Set


class Region:
    """A group of 9 cells (row, column, or box)."""
    def __init__(self, rtype: str, index: int, cells: List[Tuple[int, int]]):
        self.type = rtype    # 'row', 'col', 'box'
        self.index = index   # 1-based display index
        self.cells = cells   # list of (row, col) tuples

    def __repr__(self):
        return f"Region({self.type} {self.index})"


class Grid:
    """
    9x9 Sudoku grid.
    values[r][c]     : int, 0 = empty, 1-9 = filled
    candidates[r][c] : set of ints, possible values for empty cells
    """

    def __init__(self, values=None):
        self.values = [[0] * 9 for _ in range(9)]
        # Start with all candidates available for every cell
        self.candidates = [[set(range(1, 10)) for _ in range(9)] for _ in range(9)]
        self._build_regions()

        if values is not None:
            self._load(values)

    # ------------------------------------------------------------------
    # Initialization helpers
    # ------------------------------------------------------------------

    def _build_regions(self):
        """Pre-build all 27 regions for fast lookup."""
        self.rows = [
            Region('row', r + 1, [(r, c) for c in range(9)])
            for r in range(9)
        ]
        self.cols = [
            Region('col', c + 1, [(r, c) for r in range(9)])
            for c in range(9)
        ]
        self.boxes = [
            Region('box', br * 3 + bc + 1,
                   [(br * 3 + dr, bc * 3 + dc) for dr in range(3) for dc in range(3)])
            for br in range(3) for bc in range(3)
        ]
        self.all_regions: List[Region] = self.rows + self.cols + self.boxes

    def _load(self, values):
        """Load from 9x9 list-of-lists or 81-char string (digits, 0/. = empty)."""
        if isinstance(values, str):
            digits = [int(c) if c != '.' else 0
                      for c in values.replace(' ', '').replace('\n', '')
                      if c.isdigit() or c == '.']
            values = [[digits[r * 9 + c] for c in range(9)] for r in range(9)]
        for r in range(9):
            for c in range(9):
                v = values[r][c]
                if v:
                    self.set_value(r, c, v)

    # ------------------------------------------------------------------
    # Core operations
    # ------------------------------------------------------------------

    def set_value(self, row: int, col: int, value: int):
        """Fill a cell with a value and propagate candidate elimination."""
        self.values[row][col] = value
        self.candidates[row][col] = set()
        # Eliminate this value from every peer (same row, col, box)
        for r, c in self._peers(row, col):
            self.candidates[r][c].discard(value)

    def eliminate(self, row: int, col: int, value: int):
        """Remove a candidate from a cell (does not fill the cell)."""
        self.candidates[row][col].discard(value)

    def _peers(self, row: int, col: int) -> Set[Tuple[int, int]]:
        """Return all cells that share a region with (row, col), excluding itself."""
        peers: Set[Tuple[int, int]] = set()
        for r in range(9):
            peers.add((r, col))
        for c in range(9):
            peers.add((row, c))
        br, bc = (row // 3) * 3, (col // 3) * 3
        for dr, dc in iproduct(range(3), range(3)):
            peers.add((br + dr, bc + dc))
        peers.discard((row, col))
        return peers

    def get_box_region(self, row: int, col: int) -> Region:
        """Return the box Region containing (row, col)."""
        return self.boxes[(row // 3) * 3 + col // 3]

    # ------------------------------------------------------------------
    # State queries
    # ------------------------------------------------------------------

    def is_solved(self) -> bool:
        return all(self.values[r][c] != 0 for r in range(9) for c in range(9))

    def is_valid(self) -> bool:
        """Check no empty cell has zero candidates."""
        for r in range(9):
            for c in range(9):
                if self.values[r][c] == 0 and len(self.candidates[r][c]) == 0:
                    return False
        return True

    def copy(self) -> 'Grid':
        g = Grid()
        g.values = [row[:] for row in self.values]
        g.candidates = [[s.copy() for s in row] for row in self.candidates]
        return g

    # ------------------------------------------------------------------
    # Display
    # ------------------------------------------------------------------

    def __str__(self) -> str:
        lines = []
        for r in range(9):
            if r % 3 == 0 and r > 0:
                lines.append('------+-------+------')
            row_str = ''
            for c in range(9):
                if c > 0 and c % 3 == 0:
                    row_str += ' | '
                elif c > 0:
                    row_str += ' '
                v = self.values[r][c]
                row_str += str(v) if v else '.'
            lines.append(row_str)
        return '\n'.join(lines)

    def to_string(self) -> str:
        """Return compact 81-char representation."""
        return ''.join(
            str(self.values[r][c]) if self.values[r][c] else '.'
            for r in range(9) for c in range(9)
        )

    @staticmethod
    def from_string(s: str) -> 'Grid':
        """Parse from 81-char string (digits and . or 0 for empty)."""
        cleaned = ''
        for c in s:
            if c.isdigit():
                cleaned += c
            elif c == '.':
                cleaned += '0'
        if len(cleaned) != 81:
            raise ValueError(f"Expected 81 digits, got {len(cleaned)}: '{s}'")
        values = [[int(cleaned[r * 9 + c]) for c in range(9)] for r in range(9)]
        return Grid(values)
