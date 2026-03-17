"""
main.py - Command-line interface for the Sudoku solver.

Three functions:
  1. Analyze  : Report the minimum difficulty level needed to solve a puzzle.
  2. Solve    : Output the complete solution directly.
  3. Step     : Interactive step-by-step walkthrough with forward/back navigation.
"""
import sys
import os

# Ensure the project root is on the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from grid import Grid
from solver import Solver, SolveStep, DIFFICULTY_NAMES
from database import PuzzleDB
from typing import List, Optional


# -----------------------------------------------------------------------
# Display helpers
# -----------------------------------------------------------------------

SEPARATOR = "=" * 35


def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')


def print_grid_with_header(grid: Grid, header: str = ""):
    print(SEPARATOR)
    if header:
        print(header)
        print()
    print(grid)
    print(SEPARATOR)


def difficulty_label(d: int) -> str:
    if d == -1:
        return "无法求解（需要更高级技术）"
    name = DIFFICULTY_NAMES.get(d, f"Level {d}")
    return f"难度 {d} — {name}"


# -----------------------------------------------------------------------
# Input parsing
# -----------------------------------------------------------------------

def parse_puzzle(s: str) -> Grid:
    """Parse an 81-char sudoku string (digits, 0 or . for empty)."""
    cleaned = ''
    for ch in s:
        if ch.isdigit():
            cleaned += ch
        elif ch == '.':
            cleaned += '0'
    if len(cleaned) != 81:
        raise ValueError(
            f"需要 81 位数字，实际得到 {len(cleaned)} 位。\n"
            f"支持格式: 纯数字串（0 或 . 表示空格）"
        )
    return Grid.from_string(cleaned)


def _db_menu(db: PuzzleDB) -> Optional[Grid]:
    """Let the user pick a puzzle from the database. Returns a Grid or None."""
    print()
    print(f"数据库: {db.summary()}")
    diffs = db.all_difficulties()
    if not diffs:
        print("  数据库为空，请先输入数独。")
        return None

    print("  可选难度:", ' / '.join(str(d) for d in diffs))
    raw = input("  请输入难度 (或 q 取消) > ").strip().lower()
    if raw == 'q':
        return None
    if not raw.isdigit() or int(raw) not in diffs:
        print(f"  ✗ 无效难度")
        return None
    diff = int(raw)

    group = db.get_by_difficulty(diff)
    print(f"  难度 {diff} 共 {len(group)} 题")
    print(f"  输入题号例如 {diff}-{len(group)}，或 r 随机选择")
    raw2 = input("  > ").strip().lower()
    if raw2 == 'r':
        record = db.get_random(diff)
    elif raw2.isdigit():
        record = db.get_by_index(diff, int(raw2))
        if record is None:
            print(f"  ✗ 题号超出范围 (1-{len(group)})")
            return None
    else:
        print("  ✗ 无效输入")
        return None

    print(f"  已加载 [{record['id']}]: {record['puzzle']}")
    return Grid.from_string(record['puzzle'])


def input_puzzle(db: PuzzleDB) -> Optional[Grid]:
    """Prompt the user to enter a puzzle."""
    print("\n请输入数独（81位，0或.表示空格）")
    print("  或输入 'db' 从数据库选题")
    print("  输入 'q' 退出")
    print()

    while True:
        raw = input("数独 > ").strip()
        if raw.lower() == 'q':
            return None

        if raw.lower() == 'db':
            result = _db_menu(db)
            if result is not None:
                return result
            continue

        try:
            grid = parse_puzzle(raw)
            return grid
        except ValueError as e:
            print(f"  ✗ 输入错误: {e}")


# -----------------------------------------------------------------------
# Function 1 — Difficulty analysis
# -----------------------------------------------------------------------

def function_analyze(grid: Grid, solver: Solver, db: PuzzleDB = None):
    """Report the minimum difficulty level needed to solve the puzzle."""
    print("\n正在分析难度...")
    d = solver.analyze_difficulty(grid)

    print()
    print_grid_with_header(grid, "输入数独:")
    print()

    if d == -1:
        print("⚠  无法用当前技术（难度 1-4）完全求解此数独。")
        print("   可能需要更高级技术（X-Wing、链式推理等）。")
        effective_d = 5
    else:
        print(f"✓  所需最高难度: {difficulty_label(d)}")
        print()
        print("难度等级说明:")
        for k, v in DIFFICULTY_NAMES.items():
            marker = " ◀" if k == d else ""
            print(f"  {k}: {v}{marker}")
        effective_d = d

    # Offer to save to database
    if db is not None:
        puzzle_str = ''.join(str(grid.values[r][c]) for r in range(9) for c in range(9))
        if db.exists(puzzle_str):
            print("\n(此题已在数据库中，无需重复添加)")
        else:
            print()
            ans = input(f"是否将此题（难度 {effective_d}）加入数据库？(y/n) > ").strip().lower()
            if ans == 'y':
                pid = db.add(puzzle_str, effective_d)
                print(f"  ✓ 已保存，题目 ID: {pid}")


# -----------------------------------------------------------------------
# Function 2 — Direct solve
# -----------------------------------------------------------------------

def function_solve(grid: Grid, solver: Solver):
    """Solve and display the complete answer."""
    print("\n正在求解...")

    print_grid_with_header(grid, "输入数独:")
    print()

    solved = solver.solve(grid)
    if solved is None:
        print("⚠  无法用当前技术（难度 1-4）完全求解此数独。")
    else:
        print_grid_with_header(solved, "最终答案:")
        print("✓  求解完成！")


# -----------------------------------------------------------------------
# Function 3 — Step-by-step interactive
# -----------------------------------------------------------------------

def render_candidates_grid(grid: Grid, hint=None) -> str:
    """
    Render the grid with pencil marks showing remaining candidates.

    Each empty cell is displayed as a 3×3 sub-block:
      row 0 → candidates 1 2 3
      row 1 → candidates 4 5 6
      row 2 → candidates 7 8 9

    Spacing:
      Within a cell    : 1 space between each candidate  →  "1 2 3"  (5 chars)
      Between cells    : 3 spaces within the same box
      Between boxes    : "  |  "  (2 spaces, pipe, 2 spaces)

    Hint markers:
      [ v ]  — cell just filled by a direct hint
       x     — candidate just eliminated by this step
      digit  — candidate still present
       .     — position not a candidate (was already absent)
    """
    # Collect what to highlight from the hint
    elim_set: set = set()   # (row, col, value) eliminated in this step
    set_cell = None          # (row, col, value) directly set in this step

    if hint is not None:
        if hint.cell_value:
            set_cell = hint.cell_value
        for r, c, v in hint.eliminations:
            elim_set.add((r, c, v))

    # Spacing constants
    INNER_SEP = ' '      # between the 3 candidates within one cell (→ 5-char cell)
    CELL_SEP  = '   '    # between cells inside the same box (3 spaces)
    BOX_SEP   = '  |  '  # between boxes (2 + pipe + 2)
    CELL_W    = 5        # width of one rendered cell: "d d d"

    lines = []

    for row in range(9):
        sub = ['', '', '']   # 3 display lines for this row of cells

        for col in range(9):
            # Column separator
            if col > 0:
                sep = BOX_SEP if col % 3 == 0 else CELL_SEP
                sub[0] += sep
                sub[1] += sep
                sub[2] += sep

            v = grid.values[row][col]

            if v != 0:
                # Filled cell (5 chars wide)
                if set_cell and set_cell == (row, col, v):
                    # Just set this step → show with brackets
                    sub[0] += '     '
                    sub[1] += f'[ {v} ]'
                    sub[2] += '     '
                else:
                    sub[0] += '     '
                    sub[1] += f'  {v}  '
                    sub[2] += '     '
            else:
                # Empty cell — render each sub-row of candidates
                cands = grid.candidates[row][col]
                for i in range(3):
                    chars = []
                    for j in range(3):
                        cand = i * 3 + j + 1
                        if (row, col, cand) in elim_set:
                            chars.append('x')        # just eliminated
                        elif cand in cands:
                            chars.append(str(cand))  # still a candidate
                        else:
                            chars.append('.')        # not a candidate
                    sub[i] += INNER_SEP.join(chars)  # "1 2 3" style

        lines.extend(sub)

        # Horizontal separators
        if row < 8:
            if (row + 1) % 3 == 0:
                lines.append('-' * len(sub[0]))  # box boundary
            else:
                lines.append('')                 # blank line between rows within a box

    return '\n'.join(lines)


def print_step(idx: int, steps: List[SolveStep], initial_grid: Grid,
               show_candidates: bool = False):
    """Display the current solving state in normal or candidate view."""
    total = len(steps)

    if idx == 0:
        current_grid = initial_grid
        current_hint = None
        header = f"初始状态  (第 0/{total} 步)"
    else:
        step = steps[idx - 1]
        current_hint = step.hint
        header = (f"第 {idx}/{total} 步  |  "
                  f"{current_hint.technique}  (难度 {current_hint.difficulty})")
        current_grid = step.grid_after

    view_tag = " [候选数视图]" if show_candidates else ""
    print(SEPARATOR)
    print(header + view_tag)
    print()

    if show_candidates:
        print(render_candidates_grid(current_grid, current_hint))
    else:
        print(current_grid)

    print(SEPARATOR)

    if current_hint:
        print(f"说明: {current_hint.description}")
        if not current_hint.is_direct() and current_hint.eliminations:
            print(f"      (候选数视图中 x = 已消去的候选数，共 {len(current_hint.eliminations)} 个)")
    print()


def function_step(grid: Grid, solver: Solver):
    """Interactive step-by-step solving."""
    print("\n正在生成求解步骤...")
    steps = solver.generate_steps(grid)
    total = len(steps)

    if total == 0:
        if grid.is_solved():
            print("数独已完成！")
        else:
            print("⚠  无法用当前技术求解此数独。")
        return

    last_grid = steps[-1].grid_after if steps else grid
    solved = last_grid.is_solved()
    print(f"共生成 {total} 步{'（完全求解）' if solved else '（部分求解，需更高级技术）'}")
    print()

    idx = 0               # 0 = initial state, 1..total = after each step
    show_candidates = False

    while True:
        print_step(idx, steps, grid, show_candidates)

        # Build navigation options
        options = []
        if idx < total:
            options.append("n  下一步")
        if idx > 0:
            options.append("p  上一步")
        options.append(f"g  跳转(0-{total})")
        view_label = "普通视图" if show_candidates else "候选数视图"
        options.append(f"c  切换为{view_label}")
        options.append("q  返回")

        print("  |  ".join(options))
        cmd = input("> ").strip().lower()

        if cmd == 'c':
            show_candidates = not show_candidates
        elif cmd in ('n', 'next', '') and idx < total:
            idx += 1
        elif cmd in ('p', 'prev', 'back', 'b') and idx > 0:
            idx -= 1
        elif cmd == 'g':
            raw = input(f"  跳到第几步 (0-{total})? ").strip()
            if raw.isdigit():
                target = int(raw)
                if 0 <= target <= total:
                    idx = target
                else:
                    print(f"  请输入 0 到 {total} 之间的数字")
        elif cmd == 'q':
            break
        elif cmd.isdigit():
            target = int(cmd)
            if 0 <= target <= total:
                idx = target
            else:
                print(f"  请输入 0 到 {total} 之间的数字")


# -----------------------------------------------------------------------
# Main menu
# -----------------------------------------------------------------------

def main():
    solver = Solver()
    db = PuzzleDB()

    print()
    print("╔══════════════════════════════════╗")
    print("║      数独求解器  Sudoku Solver    ║")
    print("║  技术: Single / Lock / Naked / Hidden  ║")
    print("╚══════════════════════════════════╝")

    grid: Optional[Grid] = None

    while True:
        # Always need a puzzle loaded first
        if grid is None:
            grid = input_puzzle(db)
            if grid is None:
                print("再见！")
                break
            print()
            print_grid_with_header(grid, "当前数独:")

        print()
        print("请选择功能:")
        print("  1  分析难度（输出所需最高难度等级）")
        print("  2  直接求解（输出最终答案）")
        print("  3  逐步求解（前进 / 返回 导航）")
        print("  r  重新输入数独")
        print("  q  退出")
        print()

        choice = input("选择 > ").strip().lower()

        if choice == '1':
            function_analyze(grid, solver, db)
        elif choice == '2':
            function_solve(grid, solver)
        elif choice == '3':
            function_step(grid, solver)
        elif choice in ('r', 'new'):
            grid = None
        elif choice == 'q':
            print("再见！")
            break
        else:
            print("  请输入 1 / 2 / 3 / r / q")


if __name__ == '__main__':
    main()
