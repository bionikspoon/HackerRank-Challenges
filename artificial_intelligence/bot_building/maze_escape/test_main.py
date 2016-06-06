# coding=utf-8
from itertools import chain
from textwrap import dedent

import pytest

from .main import (
    Board, Dimensions, Cell, Coord, Delta, InvalidTarget, Bot, MOVE, Cartesian
)


# FIXTURES
# ============================================================================
@pytest.fixture
def board1():
    grid = dedent("""
        #####
        #---#
        #-b-#
        e---#
        #####
    """)[1:-1]

    return Board.from_str(grid)


@pytest.fixture
def board2():
    grid = dedent("""
        #######
        #--#--#
        #--#-b#
        #--#--#
        e-----#
        #-----#
        #######
    """)[1:-1]

    return Board.from_str(grid)


# Board.init
# ============================================================================
def test_board_has_initial_state(board2):
    assert board2.state[0][0] == Cell(0, 0, '#')
    assert board2.state[6][6] == Cell(6, 6, '#')
    assert board2.dimensions == Dimensions(7, 7)


def test_board_state_property(board1):
    assert board1.state == [
        [Cell(0, 0, '#'), Cell(0, 1, '#'), Cell(0, 2, '#'), Cell(0, 3, '#'), Cell(0, 4, '#')],
        [Cell(1, 0, '#'), Cell(1, 1, '-'), Cell(1, 2, '-'), Cell(1, 3, '-'), Cell(1, 4, '#')],
        [Cell(2, 0, '#'), Cell(2, 1, '-'), Cell(2, 2, 'b'), Cell(2, 3, '-'), Cell(2, 4, '#')],
        [Cell(3, 0, 'e'), Cell(3, 1, '-'), Cell(3, 2, '-'), Cell(3, 3, '-'), Cell(3, 4, '#')],
        [Cell(4, 0, '#'), Cell(4, 1, '#'), Cell(4, 2, '#'), Cell(4, 3, '#'), Cell(4, 4, '#')]
    ]


# Board.str
# ============================================================================
def test_board_str_shows_board(board2):
    grid = dedent("""
        #######
        #--#--#
        #--#-b#
        #--#--#
        e-----#
        #-----#
        #######
    """)[1:-1]

    assert str(board2) == grid


# Board.iter
# ============================================================================
def test_board_can_iterate_cells(board1):
    assert list(board1) == [
        Cell(0, 0, '#'), Cell(0, 1, '#'), Cell(0, 2, '#'), Cell(0, 3, '#'), Cell(0, 4, '#'),
        Cell(1, 0, '#'), Cell(1, 1, '-'), Cell(1, 2, '-'), Cell(1, 3, '-'), Cell(1, 4, '#'),
        Cell(2, 0, '#'), Cell(2, 1, '-'), Cell(2, 2, 'b'), Cell(2, 3, '-'), Cell(2, 4, '#'),
        Cell(3, 0, 'e'), Cell(3, 1, '-'), Cell(3, 2, '-'), Cell(3, 3, '-'), Cell(3, 4, '#'),
        Cell(4, 0, '#'), Cell(4, 1, '#'), Cell(4, 2, '#'), Cell(4, 3, '#'), Cell(4, 4, '#'),
    ]


# Board.iter_box
# ============================================================================
def test_board_iter_box(board1):
    assert list(board1.iter_box(Coord(1, 1), Dimensions(3, 3))) == [
        Cell(1, 1, '-'), Cell(1, 2, '-'), Cell(1, 3, '-'),
        Cell(2, 1, '-'), Cell(2, 2, 'b'), Cell(2, 3, '-'),
        Cell(3, 1, '-'), Cell(3, 2, '-'), Cell(3, 3, '-'),
    ]


# Board.filter
# ============================================================================
def test_board_can_iterate_filtered_cells(board1):
    assert list(board1.filter('-')) == [
        Cell(1, 1, '-'),
        Cell(1, 2, '-'),
        Cell(1, 3, '-'),
        Cell(2, 1, '-'),
        Cell(2, 3, '-'),
        Cell(3, 1, '-'),
        Cell(3, 2, '-'),
        Cell(3, 3, '-'),
    ]


# Board.find
# ============================================================================
@pytest.mark.parametrize('uid, expected', [
    ('b', Cell(2, 2, 'b')),
    ('e', Cell(3, 0, 'e')),
    ('q', None),
])
def test_board_find_cell_by_id(board1, uid, expected):
    assert board1.find(uid, None) == expected


def test_board_find_cell_by_coord(board1):
    assert board1.find(Coord(2, 2)) == Cell(2, 2, 'b')


def test_board_find_cell_by_cell(board1):
    assert board1.find(Cell(2, 2, 'b')) == Cell(2, 2, 'b')


def test_board_find_cell_by_delta_raises(board1):
    with pytest.raises(InvalidTarget):
        board1.find(Delta(-1, -1))


# Board.set
# ============================================================================
# test set cell value
def test_board_set_cell_value(board1):
    coord = Coord(2, 2)
    board1.set(coord, 'm')
    assert board1.find(coord).value == 'm'


# Board.is_valid
# ============================================================================
@pytest.mark.parametrize('target, expected', [
    (Coord(1, 1), True),
    (Cell(1, 1, 'b'), True),
    (Delta(1, 1), False),
    (Coord(-1, 1), False),
    (Coord(1, -1), False),
    (Coord(5, 1), False),
    (Coord(1, 5), False),
    ((1, 1), False),
    ('b', False),
])
def test_board_can_validate_coordinates(board1, target, expected):
    assert board1.is_valid(target) is expected


# Board.fork
# ============================================================================
def test_board_can_change_forked_board(board1):
    coord = Coord(2, 2)
    board2 = board1.fork()
    board2.set(coord, 'm')
    assert board2.find(coord).value == 'm'
    assert board1.find(coord).value == 'b'


# Board.move
# ============================================================================
def test_board_can_move_cells(board1):
    start, end = Coord(2, 2), Coord(2, 3)
    board1.move(start, end)

    assert board1.find(start).value == '-'
    assert board1.find(end).value == 'b'


def test_board_can_move_cell_by_delta(board1):
    start, delta, end = Coord(2, 2), Delta(-1, 0), Coord(1, 2)

    board1.move(start, delta)

    assert board1.find(start).value == '-'
    assert board1.find(end).value == 'b'


@pytest.mark.parametrize('direction, expected', [
    ('LEFT', Coord(2, 1)), ('RIGHT', Coord(2, 3)), ('UP', Coord(1, 2)), ('DOWN', Coord(3, 2)),
])
def test_board_can_move_right_left_up_and_down(board1, direction, expected):
    bot_coord = Coord(2, 2)
    delta = MOVE[direction]

    board1.move(bot_coord, delta)

    assert board1.find(bot_coord).value == '-'
    assert board1.find(expected).value == 'b'


def test_board_it_will_not_move_to_a_blocked_cell(board1):
    coord = Coord(1, 1)
    delta = MOVE['LEFT']

    with pytest.raises(InvalidTarget):
        board1.move(coord, delta)


# Bot.ini
# ============================================================================
def test_bot_initializes_with_position_and_uid(board1):
    bot_coord = Coord(2, 2)
    bot = Bot(board1, position=bot_coord, uid='m')

    assert bot.board is board1
    assert bot.uid is 'm'
    assert bot.cell == Cell(2, 2, 'm')


def test_bot_initializes_with_defaults(board1):
    bot = Bot(board1)

    assert bot.uid is 'b'
    assert bot.cell == Cell(2, 2, 'b')


# Bot.move
# ============================================================================
def test_bot_can_move(board1):
    bot = Bot(board1)

    bot.move('UP')

    assert board1.find(Coord(2, 2)).value == '-'
    assert board1.find(Coord(1, 2)).value == 'b'


# Bot.fork
# ============================================================================
def test_bot_can_fork_and_move(board1):
    bot0 = Bot(board1)

    bot1 = bot0.fork('UP')

    assert board1.find(Coord(2, 2)).value == 'b'
    assert board1.find(Coord(1, 2)).value == 'b UP'

    bot1.fork('LEFT')

    assert board1.find(Coord(2, 2)).value == 'b'
    assert board1.find(Coord(1, 2)).value == 'b UP'
    assert board1.find(Coord(1, 1)).value == 'b UP LEFT'


def test_bot_forks_are_added_to_registry(board1):
    bot0 = Bot(board1)

    bot1 = bot0.fork('UP')
    bot2 = bot1.fork('LEFT')

    assert bot0.registry == {
        Coord(2, 2): bot0,
        Coord(1, 2): bot1,
        Coord(1, 1): bot2,
    }


# Bot.ping
# ============================================================================
def test_bot_can_ping_cell(board1):
    bot = Bot(board1)

    bots = list(bot.ping())
    assert [bot.uid for bot in bots] == ['b UP', 'b RIGHT', 'b DOWN', 'b LEFT']

    bots = list(chain.from_iterable(list(bot.ping()) for bot in bots))
    bots = list(chain.from_iterable(list(bot.ping()) for bot in bots))
    assert [bot.uid for bot in bots] == ['b DOWN LEFT LEFT']


# Bot.find_path
# ============================================================================
def test_bot_can_find_path_to_exit_1(board1):
    bot = Bot(board1)

    assert bot.find_path('e') == ['DOWN', 'LEFT', 'LEFT']


def test_bot_can_find_path_to_exit_2(board2):
    bot = Bot(board2)

    assert bot.find_path('e') == ['DOWN', 'DOWN', 'LEFT', 'LEFT', 'LEFT', 'LEFT', 'LEFT']


def test_bot_can_find_path_to_exit_3():
    grid = dedent("""
        #######
        #--#b-#
        #--#--#
        #--#--#
        e-----#
        #-----#
        #######
    """)[1:-1]

    board = Board.from_str(grid)
    bot = Bot(board)

    assert bot.find_path('e') == ['DOWN', 'DOWN', 'DOWN', 'LEFT', 'LEFT', 'LEFT', 'LEFT']


def test_bot_find_path_does_not_affect_board_or_bot(board2):
    bot = Bot(board2)

    bot.find_path('e')

    grid = dedent("""
        #######
        #--#--#
        #--#-b#
        #--#--#
        e-----#
        #-----#
        #######
    """)[1:-1]

    assert str(board2) == grid
    assert bot.uid == 'b'


# Cartesian.init
# ============================================================================
def test_cartesian_initializes_with_y_and_x():
    cartesian = Cartesian(2, 2)
    assert (cartesian.y, cartesian.x) == (2, 2)


# Cartesian.eql
# ============================================================================
@pytest.mark.parametrize('cartesian, expected', [
    (Cartesian(2, 2), True),
    (Cartesian(1, 2), False),
    (Cartesian(2, 1), False),
])
def test_cartesian_is_equal_when_y_and_x_match(cartesian, expected):
    assert (Cartesian(2, 2) == cartesian) == expected


# Coord.hash
# ============================================================================
def test_cartesian_hash_includes_y_and_x():
    cartesian = Cartesian(2, 2)
    assert hash(cartesian) == hash((2, 2))


# Coord.to_cell
# ============================================================================
def test_coord_to_cell():
    coord = Coord(2, 2)
    assert coord.to_cell('b') == Cell(2, 2, 'b')


# Coord.to_coord
# ============================================================================
def test_coord_to_coord():
    coord = Coord(2, 2)
    assert coord.to_coord() == coord


# Coord.to_delta
# ============================================================================
def test_coord_to_delta_calculates_delta_to_target():
    coord = Coord(2, 2)

    assert coord.to_delta(Coord(4, 4)) == Delta(2, 2)


def test_coord_to_delta_handles_delta():
    coord = Coord(2, 2)
    delta = Delta(2, 2)

    assert coord.to_delta(delta) is delta


# Coord.to_delta
# ============================================================================
def test_coord_get_distance_calculates_moves_to_dest():
    coord = Coord(2, 2)
    delta = Delta(2, 2)

    assert coord.get_distance(delta) == 4


# Cell.init
# ============================================================================
def test_cell_initializes_with_y_x_and_value():
    cell = Cell(2, 2, 'b')

    assert (cell.y, cell.x, cell.value) == (2, 2, 'b')


# Cell.to_cell
# ============================================================================
def test_cell_to_cell_returns_self():
    cell = Cell(2, 2, 'b')

    assert cell.to_cell() is cell


@pytest.mark.parametrize('cell, expected', [
    (Cell(2, 2, 'b'), True),
    (Cell(1, 2, 'b'), False),
    (Cell(2, 1, 'b'), False),
    (Cell(2, 2, 'c'), False),
])
def test_cell_is_equal_when_y_x_and_value_match(cell, expected):
    assert (Cell(2, 2, 'b') == cell) == expected


# Delta.resolve
# ============================================================================
def test_delta_resolves_coord_from_start():
    coord = Coord(2, 2)
    delta = Delta(-1, 3)
    assert delta.resolve(coord) == Coord(1, 5)


# Board.init
# ============================================================================
def test_partial_board_sets_bot_position():
    state = dedent("""
        #--
        #--
        #--
    """)[1:-1]
    board = Board.from_str(state)
    board.set(Coord(1, 1), 'b')
    assert board.find('b') == Cell(1, 1, 'b')


# Board.from_str
# ============================================================================
def test_partial_board_from_input_parses_prev_state():
    state = dedent("""
        UP
        2
        #--
        #b-
        ###
    """)[1:-1]
    expected = dedent("""
        #b-
        #--
        ###
    """)[1:-1]
    board = Board.from_input(state)

    assert str(board) == expected


def test_partial_board_from_input_parses_next_style_state():
    state = dedent("""
        2
        #--
        #--
        #--
    """)[1:-1]
    expected = dedent("""
        #--
        #b-
        #--
    """)[1:-1]
    board = Board.from_input(state)

    assert str(board) == expected


# Board.with_move
# ============================================================================
def test_partial_board_with_move_creates_a_board():
    state = dedent("""
        #--
        #--
        #--
    """)[1:-1]
    expected = dedent("""
        #--
        #b-
        #--
    """)[1:-1]
    board = Board.with_move(state)

    assert str(board) == expected


def test_partial_board_with_move_moves_bot():
    state = dedent("""
        #--
        #b-
        ###
    """)[1:-1]
    expected = dedent("""
        #b-
        #--
        ###
    """)[1:-1]
    board = Board.with_move(state, direction='UP')
    assert str(board) == expected


def test_partial_board_with_move_rotate_and_moves_bot():
    state = dedent("""
        #--
        #b-
        ###
    """)[1:-1]
    expected = dedent("""
        -b#
        --#
        ###
    """)[1:-1]
    board = Board.with_move(state, direction='RIGHT')
    assert str(board) == expected


# Board.rotate
# ============================================================================
@pytest.mark.parametrize('direction, expected', [
    ('UP', dedent("""
        123
        456
        789
    """)[1:-1]),
    ('RIGHT', dedent("""
        369
        258
        147
    """)[1:-1]),
    ('DOWN', dedent("""
        987
        654
        321
    """)[1:-1]),
    ('LEFT', dedent("""
        741
        852
        963
    """)[1:-1]),
])
def test_partial_board_rotate(direction, expected):
    state = dedent("""
        123
        456
        789
    """)[1:-1]
    assert Board.rotate(state, direction) == expected


@pytest.mark.parametrize('direction, expected', [
    ('UP', dedent("""
        abcd
        efgh
        ijkl
    """)[1:-1]),
    ('RIGHT', dedent("""
        dhl
        cgk
        bfj
        aei
    """)[1:-1]),
    ('DOWN', dedent("""
        lkji
        hgfe
        dcba
    """)[1:-1]),
    ('LEFT', dedent("""
        iea
        jfb
        kgc
        lhd
    """)[1:-1]),
])
def test_partial_board_rotate_rectangle(direction, expected):
    state = dedent("""
        abcd
        efgh
        ijkl
    """)[1:-1]

    assert Board.rotate(state, direction) == expected


# Board.merge
# ============================================================================
@pytest.mark.parametrize('directions, cell, expected', [
    (['LEFT'], Cell(1, 2, 'b'), dedent("""
        o---
        o-b-
        o---
    """)[1:-1]),
    (['RIGHT'], Cell(1, 1, 'b'), dedent("""
        ---o
        -b-o
        ---o
    """)[1:-1]),
    (['UP'], Cell(2, 1, 'b'), dedent("""
        ooo
        ---
        -b-
        ---
    """)[1:-1]),
    (['DOWN'], Cell(1, 1, 'b'), dedent("""
        ---
        -b-
        ---
        ooo
    """)[1:-1]),
    (['UP', 'LEFT', 'DOWN', 'RIGHT', 'LEFT'], Cell(2, 3, 'b'), dedent("""
        oooooo
        oo---o
        oo-b-o
        oo---o
        oooooo
    """)[1:-1]),
])
def test_partial_board_pad_left(directions, cell, expected):
    state = dedent("""
        2
        ---
        ---
        ---
    """)[1:-1]

    board = Board.from_input(state)
    board.pad(directions)

    assert str(board) == expected
    assert board.find('b') == cell


# Board.merge
# ============================================================================
@pytest.mark.parametrize('prev_state, next_state, expected', [
    # CASE
    (dedent("""
            UP
            2
            #--
            #b-
            ###
        """)[1:-1],
     dedent("""
            2
            #--
            #--
            #--
        """)[1:-1],
     dedent("""
            #--
            #b-
            #--
            ###
        """)[1:-1]
     ),

    # CASE
    (dedent("""
            RIGHT
            2
            ###
            #b-
            #--
        """)[1:-1],
     dedent("""
            2
            #--
            #--
            #--
        """)[1:-1],
     dedent("""
            #--
            #b-
            #--
            ###
        """)[1:-1]
     ),

    # CASE
    (dedent("""
            LEFT
            2
            #--
            eb-
            #--
            ###
        """)[1:-1],
     dedent("""
            2
            ###
            #e#
            ---
        """)[1:-1],
     dedent("""
            o###
            ##b#
            #---
            #---
        """)[1:-1]
     ),
])
def test_partial_board_merge_two_boards(prev_state, next_state, expected):
    prev_board = Board.from_input(prev_state)
    next_board = Board.from_input(next_state)

    prev_board.merge(next_board)

    assert str(prev_board) == expected


# test bot find position
def test_bot_find_position():
    master = dedent("""
        #######
        #--#--#
        #--#--#
        #--#--#
        e-----#
        #-----#
        #######
    """)[1:-1]
    state = dedent("""
        2
        #--
        #--
        #--
        #--
    """)[1:-1]
    board = Board.from_input(state)
    bot = Bot(board)

    assert bot.find_move_from_position(master) == 'RIGHT'


# test bot find position
def test_bot_next_move():
    master = dedent("""
        #######
        #--#--#
        #--#--#
        #--#--#
        e-----#
        #-----#
        #######
    """)[1:-1]
    state = dedent("""
        2
        #--
        #--
        #--
    """)[1:-1]
    board = Board.from_input(state)
    bot = Bot(board)

    assert bot.next_move(master) == 'RIGHT'
