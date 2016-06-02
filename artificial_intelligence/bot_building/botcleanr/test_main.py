# test print_board
from textwrap import dedent

import pytest

from .main import Board, Coord, Cell, Delta, MOVE_LEFT, MOVE_RIGHT, MOVE_UP, MOVE_DOWN, InvalidMove, NoValidMove, Bot, \
    next_move


@pytest.fixture
def board():
    grid_size = 3
    grid = dedent("""
        ---
        -m-
        p--
    """[1:]).rstrip()

    return Board(grid_size, grid)


@pytest.fixture
def board2():
    grid_size = 5
    grid = dedent("""
        b---d
        -d--d
        --dd-
        --d--
        ----d
    """[1:]).rstrip()

    return Board(grid_size, grid)


def test_pformat_board_format(board):
    grid = dedent("""
        ---
        -m-
        p--
    """[1:]).rstrip()

    assert board.pformat() == grid


def test_board_state_is_a_list_of_lists(board):
    assert board._state == [['-', '-', '-'], ['-', 'm', '-'], ['p', '-', '-']]


def test_can_find_character_coordinates_for_m(board):
    assert board.find('m') == Cell(1, 1, 'm')


def test_can_find_character_coordinates_for_p(board):
    assert board.find('p') == Cell(2, 0, 'p')


def test_returns_none_if_not_found(board):
    assert board.find('q') is None


def test_can_iterate_state(board):
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

    assert tuple(board.iter_state()) == expected


@pytest.mark.parametrize('coord,cell', [(Coord(2, 0), Cell(2, 0, 'p')), (Coord(1, 1), Cell(1, 1, 'm'))])
def test_can_lookup_cell_by_coordinates(board, coord, cell):
    assert board.find(coord) == cell


def test_can_set_individual_cells(board):
    coord = Coord(1, 1)
    board.set_cell(coord, '-')
    assert board.find(coord).value == '-'


def test_can_move_cells(board):
    board.move(Coord(1, 1), Coord(1, 2))
    assert board.find(Coord(1, 1)).value == '-'
    assert board.find(Coord(1, 2)).value == 'm'


def test_can_move_cells_by_delta(board):
    board.move(Coord(1, 1), Delta(-1, 0))
    assert board.find(Coord(1, 1)).value == '-'
    assert board.find(Coord(0, 1)).value == 'm'


@pytest.mark.parametrize('delta, expect', [
    (MOVE_LEFT, Coord(1, 0)),
    (MOVE_RIGHT, Coord(1, 2)),
    (MOVE_UP, Coord(0, 1)),
    (MOVE_DOWN, Coord(2, 1)),
])
def test_can_move_left_right_up_and_down(board, delta, expect):
    board.move(Coord(1, 1), delta)
    assert board.find(Coord(1, 1)).value == '-'
    assert board.find(expect).value == 'm'


@pytest.mark.parametrize('delta', [MOVE_LEFT, MOVE_DOWN])
def test_can_only_move_to_valid_cells(board, delta):
    with pytest.raises(InvalidMove):
        board.move(Coord(2, 0), delta)


def test_it_can_find_the_delta_from_a_character_to_a_target(board):
    assert board.find_delta('m', 'p') == Delta(1, -1)


def test_it_raises_when_character_or_target_can_t_be_found(board):
    board.move(Coord(1, 1), Coord(2, 0))
    with pytest.raises(NoValidMove):
        board.find_delta('m', 'p')


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
    bot = Bot(board2, 'b')
    assert bot.get_proximity(target) == expected


def test_it_can_choose_a_target(board2):
    bot = Bot(board2, 'b')
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
    grid_size = 5
    grid = dedent("""
        ----d
        -----
        --bd-
        --dd-
        dd--d
    """[1:]).rstrip()

    board = Board(grid_size, grid)
    bot = Bot(board, 'b')
    targets = board.findall('d')
    assert bot.choose_target(targets) == Cell(2, 3, 'd')


def test_it_prefers_a_target_in_its_quadrant_1():
    grid_size = 5
    grid = dedent("""
        ----d
        -----
        ---b-
        --dd-
        dd--d
    """[1:]).rstrip()

    board = Board(grid_size, grid)
    bot = Bot(board, 'b')
    targets = board.findall('d')
    assert bot.choose_target(targets) == Cell(0, 4, 'd')


def test_it_returns_next_move():
    grid = dedent("""
        ----d
        -----
        ---b-
        --dd-
        dd--d
    """[1:]).rstrip()

    assert next_move(2, 3, grid) == 'UP'


def test_it_prefers_corners():
    grid = dedent("""
        -----
        -----
        -----
        --ddb
        dd--d
    """[1:]).rstrip()

    assert next_move(3, 4, grid) == 'DOWN'


def test_it_suggests_a_move(board2):
    bot = Bot(board2, 'b')
    assert bot.suggest_move('d') == MOVE_DOWN
