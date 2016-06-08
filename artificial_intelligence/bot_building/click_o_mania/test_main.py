# coding=utf-8
from textwrap import dedent
from .main import BaseBoard, debugf


# FIXTURES
# ============================================================================

# Board.init
# ============================================================================
def test_board_init():
    state = dedent("""
        BRBB
        RRYY
        YRBY
        BRRY
        YRRB
    """)[1:-1]

    board = BaseBoard(5, 4, state)

    assert board.y == 5
    assert board.x == 4

    expected = {
        (0, 0): 'B', (0, 1): 'R', (0, 2): 'B', (0, 3): 'B',
        (1, 0): 'R', (1, 1): 'R', (1, 2): 'Y', (1, 3): 'Y',
        (2, 0): 'Y', (2, 1): 'R', (2, 2): 'B', (2, 3): 'Y',
        (3, 0): 'B', (3, 1): 'R', (3, 2): 'R', (3, 3): 'Y',
        (4, 0): 'Y', (4, 1): 'R', (4, 2): 'R', (4, 3): 'B',
    }
    debugf(board.state)
    assert board.state == expected
