"""
base.py - Base classes for all Sudoku solving techniques.

To add a new technique:
1. Create a subclass of Technique
2. Implement find_hints(grid) -> List[Hint]
3. Register it in solver.py DEFAULT_TECHNIQUES (in difficulty order)
"""
from dataclasses import dataclass, field
from typing import List, Optional, Tuple


@dataclass
class Hint:
    """
    Represents one solving step produced by a technique.

    A hint is either:
    - A direct hint: sets a cell to a value (cell_value is set)
    - An elimination hint: removes candidates (eliminations is non-empty)
    """
    technique: str           # Display name of the technique
    difficulty: int          # Difficulty level (1=easiest, higher=harder)
    description: str         # Human-readable explanation

    # For direct hints (set a cell value)
    cell_value: Optional[Tuple[int, int, int]] = None  # (row, col, value)

    # For elimination hints (remove candidates without filling cells)
    eliminations: List[Tuple[int, int, int]] = field(default_factory=list)
    # Each entry: (row, col, value_to_remove)

    def is_direct(self) -> bool:
        return self.cell_value is not None

    def summary(self) -> str:
        if self.is_direct():
            r, c, v = self.cell_value
            return f"[{self.technique}] R{r+1}C{c+1} = {v}"
        else:
            elim_str = ', '.join(f"R{r+1}C{c+1}≠{v}" for r, c, v in self.eliminations[:3])
            if len(self.eliminations) > 3:
                elim_str += f" ... (+{len(self.eliminations)-3} more)"
            return f"[{self.technique}] Eliminate: {elim_str}"


class Technique:
    """
    Abstract base class for all Sudoku solving techniques.

    Subclasses must define:
        name       : str   - display name
        difficulty : int   - relative difficulty (1 = easiest)
    And implement:
        find_hints(grid) -> List[Hint]
    """
    name: str = "Base"
    difficulty: int = 0

    def find_hints(self, grid) -> List[Hint]:
        """
        Search the grid for applicable hints.
        Returns a list of all found hints (may be empty).
        """
        raise NotImplementedError(f"{self.__class__.__name__} must implement find_hints()")

    def find_first_hint(self, grid) -> Optional[Hint]:
        """
        Return the first applicable hint, or None.
        Override for more efficient single-hint search.
        """
        hints = self.find_hints(grid)
        return hints[0] if hints else None

    def __repr__(self):
        return f"{self.__class__.__name__}(difficulty={self.difficulty})"
