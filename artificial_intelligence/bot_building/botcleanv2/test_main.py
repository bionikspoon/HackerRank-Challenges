# coding=utf-8
from textwrap import dedent

import pytest

from .main import (
    Board, Coord, Cell, Delta, MOVE_LEFT, MOVE_RIGHT, MOVE_UP, MOVE_DOWN, InvalidMove, NoValidMove, Bot, next_move,
    Dimensions, utils,
    parse_input)


# FIXTURES
# ============================================================================
@pytest.fixture
def board1():
    dimensions = Dimensions(3, 3)
    grid = dedent("""
        ---
        -m-
        p--
    """[1:])[:-1]

    return Board(dimensions, grid)


@pytest.fixture
def board2():
    dimensions = Dimensions(5, 5)
    grid = dedent("""
        b---d
        -d--d
        --dd-
        --d--
        ----d
    """[1:])[:-1]

    return Board(dimensions, grid)


@pytest.fixture
def board3():
    dimensions = Dimensions(5, 5)
    grid = dedent("""
        b-ooo
        -dooo
        ooooo
        ooooo
        ooooo
    """[1:])[:-1]

    return Board(dimensions, grid)


# Board.state
# ============================================================================

def test_state_is_a_list_of_lists_of_cells(board1):
    assert board1.state == [
        [Cell(y=0, x=0, value='-'), Cell(y=0, x=1, value='-'), Cell(y=0, x=2, value='-')],
        [Cell(y=1, x=0, value='-'), Cell(y=1, x=1, value='m'), Cell(y=1, x=2, value='-')],
        [Cell(y=2, x=0, value='p'), Cell(y=2, x=1, value='-'), Cell(y=2, x=2, value='-')],
    ]


# Board.find
# ============================================================================
def test_can_find_cell_by_letter_m(board1):
    assert board1.find('m') == Cell(1, 1, 'm')


def test_can_find_cell_by_letter_p(board1):
    assert board1.find('p') == Cell(2, 0, 'p')


def test_find_returns_none_if_not_found(board1):
    assert board1.find('q') is None


@pytest.mark.parametrize('coord, cell', [(Coord(2, 0), Cell(2, 0, 'p')), (Coord(1, 1), Cell(1, 1, 'm'))])
def test_can_find_cell_by_coordinates(board1, coord, cell):
    assert board1.find(coord) == cell


# Board.iter_cells
# ============================================================================

def test_can_iterate_cells(board1):
    expected = (
        Cell(y=0, x=0, value='-'),
        Cell(y=0, x=1, value='-'),
        Cell(y=0, x=2, value='-'),
        Cell(y=1, x=0, value='-'),
        Cell(y=1, x=1, value='m'),
        Cell(y=1, x=2, value='-'),
        Cell(y=2, x=0, value='p'),
        Cell(y=2, x=1, value='-'),
        Cell(y=2, x=2, value='-')
    )

    assert tuple(board1.iter_cells()) == expected


# Board.iter_cells_by_quadrant
# ============================================================================
@pytest.mark.parametrize('quadrant, expected', [
    (1, [
        Cell(y=0, x=0, value='b'),
        Cell(y=0, x=1, value='-'),
        Cell(y=1, x=0, value='-'),
        Cell(y=1, x=1, value='d'),
    ]),
    (2, [
        Cell(y=0, x=2, value='-'),
        Cell(y=0, x=3, value='-'),
        Cell(y=0, x=4, value='d'),
        Cell(y=1, x=2, value='-'),
        Cell(y=1, x=3, value='-'),
        Cell(y=1, x=4, value='d'),
    ]),
    (3, [
        Cell(y=2, x=2, value='d'),
        Cell(y=2, x=3, value='d'),
        Cell(y=2, x=4, value='-'),
        Cell(y=3, x=2, value='d'),
        Cell(y=3, x=3, value='-'),
        Cell(y=3, x=4, value='-'),
        Cell(y=4, x=2, value='-'),
        Cell(y=4, x=3, value='-'),
        Cell(y=4, x=4, value='d'),
    ]),
    (4, [
        Cell(y=2, x=0, value='-'),
        Cell(y=2, x=1, value='-'),
        Cell(y=3, x=0, value='-'),
        Cell(y=3, x=1, value='-'),
        Cell(y=4, x=0, value='-'),
        Cell(y=4, x=1, value='-'),
    ]),
])
def test_can_iterate_cells_by_quadrant(board2, quadrant, expected):
    assert list(board2.iter_cells_by_quadrant(quadrant)) == expected


# Board.findall
# ============================================================================
def test_can_find_all(board2):
    assert board2.findall('d') == [
        Cell(y=0, x=4, value='d'),
        Cell(y=1, x=1, value='d'),
        Cell(y=1, x=4, value='d'),
        Cell(y=2, x=2, value='d'),
        Cell(y=2, x=3, value='d'),
        Cell(y=3, x=2, value='d'),
        Cell(y=4, x=4, value='d'),
    ]


# Board.findall_in_quadrant
# ============================================================================
@pytest.mark.parametrize('quadrant, expected', [
    (1, [
        Cell(y=1, x=1, value='d'),
    ]),
    (2, [
        Cell(y=0, x=4, value='d'),
        Cell(y=1, x=4, value='d'),
    ]),
    (3, [
        Cell(y=2, x=2, value='d'),
        Cell(y=2, x=3, value='d'),
        Cell(y=3, x=2, value='d'),
        Cell(y=4, x=4, value='d'),
    ]),
    (4, []),
])
def test_can_iterate_cells_by_quadrant(board2, quadrant, expected):
    assert board2.findall_in_quadrant(quadrant, 'd') == expected


# Board.set_cell
# ============================================================================
def test_can_set_individual_cells(board1):
    coord = Coord(1, 1)
    board1.set_cell(coord, '-')
    assert board1.find(coord).value == '-'


# Board.is_valid_coord
# ============================================================================
@pytest.mark.parametrize('target, expected', [
    (Coord(1, 1), True),
    (Cell(1, 1, 'm'), True),
    (Delta(1, 1), False),
    (Coord(-1, 1), False),
    (Coord(1, -1), False),
    (Coord(3, 1), False),
    (Coord(1, 3), False),
    ((1, 1), False),
    ('m', False),
])
def test_it_can_validate_coordinates(board1, target, expected):
    assert board1.is_valid_coord(target) is expected


# Board.move
# ============================================================================

def test_can_move_cells(board1):
    board1.move(Coord(1, 1), Coord(1, 2))
    assert board1.find(Coord(1, 1)).value == '-'
    assert board1.find(Coord(1, 2)).value == 'm'


def test_can_move_cells_by_delta(board1):
    board1.move(Coord(1, 1), Delta(-1, 0))
    assert board1.find(Coord(1, 1)).value == '-'
    assert board1.find(Coord(0, 1)).value == 'm'


@pytest.mark.parametrize('delta, expect', [
    (MOVE_LEFT, Coord(1, 0)),
    (MOVE_RIGHT, Coord(1, 2)),
    (MOVE_UP, Coord(0, 1)),
    (MOVE_DOWN, Coord(2, 1)),
])
def test_can_move_left_right_up_and_down(board1, delta, expect):
    board1.move(Coord(1, 1), delta)
    assert board1.find(Coord(1, 1)).value == '-'
    assert board1.find(expect).value == 'm'


@pytest.mark.parametrize('delta', [MOVE_LEFT, MOVE_DOWN])
def test_can_only_move_to_valid_cells(board1, delta):
    with pytest.raises(InvalidMove):
        board1.move(Coord(2, 0), delta)


# Board.pformat
# ============================================================================

def test_pformat_board_format(board1):
    grid = dedent("""
        ---
        -m-
        p--
    """[1:])[:-1]

    assert board1.pformat() == grid


# utils.find_delta
# ============================================================================
def test_it_can_find_delta_between_coords():
    a = Coord(1, 1)
    b = Coord(2, 0)
    assert utils.find_delta(a, b) == Delta(1, -1)


def test_it_can_find_the_delta_from_a_character_to_a_target(board1):
    assert utils.find_delta(board1.find('m'), board1.find('p')) == Delta(1, -1)


def test_it_raises_when_character_or_target_cant_be_found(board1):
    board1.move(Coord(1, 1), Coord(2, 0))
    with pytest.raises(NoValidMove):
        utils.find_delta(board1.find('m'), board1.find('p'))


# utils.resolve_delta
# ============================================================================
def test_it_resolves_delta_from_delta_to_cell():
    coord = Coord(1, 1)
    delta = Delta(-1, -1)
    assert utils.resolve_delta(coord, delta) == Coord(0, 0)


def test_it_resolves_delta_from_cell_to_cell():
    coord = Coord(1, 1)
    delta = Coord(2, 0)
    assert utils.resolve_delta(coord, delta) == Coord(2, 0)


# utils.find_distance
# ============================================================================

@pytest.mark.parametrize('target,expected', [
    (Cell(y=0, x=4, value='d'), 4),
    (Cell(y=1, x=1, value='d'), 2),
    (Cell(y=1, x=4, value='d'), 5),
    (Cell(y=2, x=2, value='d'), 4),
    (Cell(y=2, x=3, value='d'), 5),
    (Cell(y=3, x=2, value='d'), 5),
    (Cell(y=4, x=4, value='d'), 8),
])
def test_it_can_calculate_proximity(board2, target, expected):
    bot = Bot(board2)
    assert utils.find_distance(bot.cell, target) == expected


# utils.find_distance
# ============================================================================
@pytest.mark.parametrize('coord, expected', [
    (Coord(0, 0), 1),
    (Coord(0, 1), 1),
    (Coord(0, 2), 2),
    (Coord(0, 3), 2),
    (Coord(0, 4), 2),
    (Coord(1, 1), 1),
    (Coord(2, 2), 3),
    (Coord(4, 4), 3),
    (Coord(4, 1), 4),
])
def test_find_quadrants(board2, coord, expected):
    assert utils.find_cell_quadrant(board2, coord) == expected


# Bot.choose_target
# ============================================================================
def test_it_can_choose_a_target(board2):
    bot = Bot(board2)
    targets = [
        Cell(y=0, x=4, value='d'),
        Cell(y=1, x=1, value='d'),
        Cell(y=1, x=4, value='d'),
        Cell(y=2, x=2, value='d'),
        Cell(y=2, x=3, value='d'),
        Cell(y=3, x=2, value='d'),
        Cell(y=4, x=4, value='d'),
    ]
    assert bot.choose_target(targets) is targets[1]


def test_it_prefers_a_target_in_its_quadrant_0():
    data = dedent("""
        2 2
        ----d
        -----
        --bd-
        --dd-
        dd--d
    """[1:])[:-1]
    board, bot = utils.setup(*parse_input(data))

    targets = board.findall('d')
    assert bot.choose_target(targets) == Cell(2, 3, 'd')


def test_it_prefers_a_target_in_its_quadrant_1():
    data = dedent("""
        2 3
        ----d
        -----
        ---b-
        --dd-
        dd--d
    """[1:])[:-1]

    board, bot = utils.setup(*parse_input(data))
    targets = board.findall('d')
    assert bot.choose_target(targets) == Cell(3, 3, 'd')


# Bot.suggest_move
# ============================================================================
def test_it_suggests_a_move(board2):
    bot = Bot(board2, 'b')
    assert bot.suggest_move('d') == MOVE_RIGHT


# parse_input
# ============================================================================
def test_it_parses_input():
    data = dedent("""
        3 4
        ooooo
        ooooo
        ooo--
        ooo-b
        ooo--
    """[1:])[:-1]

    y, x, grid = parse_input(data)
    assert (y, x) == (3, 4)
    assert grid == dedent("""
        ooooo
        ooooo
        ooo--
        ooo-b
        ooo--
    """[1:])[:-1]


# next_move
# ============================================================================

def test_it_returns_next_move():
    data = dedent("""
        2 3
        ----d
        -----
        ---b-
        --dd-
        dd--d
    """[1:])[:-1]

    assert next_move(*parse_input(data)) == 'DOWN'


def test_it_prefers_corners():
    data = dedent("""
        3 4
        -----
        -----
        -----
        --ddb
        dd--d
    """[1:])[:-1]

    assert next_move(*parse_input(data)) == 'DOWN'


def test_it_can_clean_the_d():
    data = dedent("""
        1 1
        ---oo
        -d-oo
        ---oo
        ooooo
        ooooo
    """[1:])[:-1]

    assert next_move(*parse_input(data)) == 'CLEAN'


def test_it_will_fallback_to_revealing_o():
    data = dedent("""
        1 1
        ---oo
        -b-oo
        ---oo
        ooooo
        ooooo
    """[1:])[:-1]

    assert next_move(*parse_input(data)) == 'RIGHT'


def test_it_prefers_to_not_traverse_the_edges_blindly():
    data = dedent("""
        3 4
        ooooo
        ooooo
        ooo--
        ooo-b
        ooo--
    """[1:])[:-1]

    assert next_move(*parse_input(data)) == 'LEFT'
