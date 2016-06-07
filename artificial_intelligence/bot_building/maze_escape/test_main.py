# coding=utf-8
from io import StringIO
from itertools import chain
from textwrap import dedent

import pytest

from .main import Board, Dimensions, Cell, Coord, Delta, InvalidTarget, Bot, Cartesian


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


# Board.from_str
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


# Board.from_state
# ============================================================================
def test_board_from_state(board1):
    state = [
        [Cell(0, 0, '#'), Cell(0, 1, '#'), Cell(0, 2, '#'), Cell(0, 3, '#'), Cell(0, 4, '#')],
        [Cell(1, 0, '#'), Cell(1, 1, '-'), Cell(1, 2, '-'), Cell(1, 3, '-'), Cell(1, 4, '#')],
        [Cell(2, 0, '#'), Cell(2, 1, '-'), Cell(2, 2, 'b'), Cell(2, 3, '-'), Cell(2, 4, '#')],
        [Cell(3, 0, 'e'), Cell(3, 1, '-'), Cell(3, 2, '-'), Cell(3, 3, '-'), Cell(3, 4, '#')],
        [Cell(4, 0, '#'), Cell(4, 1, '#'), Cell(4, 2, '#'), Cell(4, 3, '#'), Cell(4, 4, '#')]
    ]
    board = Board.from_state(state)
    assert str(board) == str(board1)


# Board.from_input
# ============================================================================
def test_board_from_input():
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


# Board.load
# ============================================================================
def test_board_load_with_move():
    state = dedent("""
        UP
        #--
        #b-
        ###
    """)[1:-1]
    expected = dedent("""
        #b-
        #--
        ###
    """)[1:-1]

    with StringIO(state) as f:
        board = Board.load(f)

    assert str(board) == expected


def test_board_load_with_rotate():
    state = dedent("""
        RIGHT
        #--
        #b-
        ###
    """)[1:-1]
    expected = dedent("""
        -b#
        --#
        ###
    """)[1:-1]
    with StringIO(state) as f:
        board = Board.load(f)

    assert str(board) == expected


# Board.dimensions
# ============================================================================
def test_board_dimensions(board1):
    assert board1.dimensions == Dimensions(5, 5)


# Board.iter
# ============================================================================
def test_board_iter(board1):
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


# Board.filter
# ============================================================================
def test_board_filter(board1):
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


# Board.set
# ============================================================================
def test_board_set(board1):
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
def test_board_is_valid(board1, target, expected):
    assert board1.is_valid(target) is expected


# Board.fork
# ============================================================================
def test_board_fork(board1):
    coord = Coord(2, 2)
    board2 = board1.fork()
    board2.set(coord, 'm')
    assert board2.find(coord).value == 'm'
    assert board1.find(coord).value == 'b'


# Bot.move
# ============================================================================
def test_bot_move(board1):
    bot = Bot(board1)

    bot.move('UP')

    assert board1.find(Coord(2, 2)).value == '-'
    assert board1.find(Coord(1, 2)).value == 'b'


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


# Board.pad
# ============================================================================

@pytest.mark.parametrize('state, next_state, expected', [
    # CASE
    (dedent("""
            UP
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
def test_board_merge_two_boards(state, next_state, expected):
    with StringIO(state) as f:
        board = Board.load(f)

    next_board = Board.from_input(next_state)

    board.merge(next_board)

    assert str(board) == expected


# Board.pad
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
def test_board_pad_left(directions, cell, expected):
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


# Board.rotate
# ============================================================================
@pytest.mark.parametrize('direction, undo, expected', [
    [
        'UP',
        False,
        dedent("""
            123
            456
            789
        """)[1:-1]
    ],
    [
        'RIGHT',
        False,
        dedent("""
            369
            258
            147
        """)[1:-1]
    ],
    [
        'DOWN',
        False,
        dedent("""
            987
            654
            321
        """)[1:-1]
    ],
    [
        'LEFT',
        False,
        dedent("""
            741
            852
            963
        """)[1:-1]
    ],
    [
        'UP',
        True,
        dedent("""
            123
            456
            789
        """)[1:-1]
    ],
    [
        'LEFT',
        True,
        dedent("""
            369
            258
            147
        """)[1:-1]
    ],
    [
        'DOWN',
        True,
        dedent("""
            987
            654
            321
        """)[1:-1]
    ],
    [
        'RIGHT',
        True,
        dedent("""
            741
            852
            963
        """)[1:-1]
    ],
])
def test_board_rotate(direction, undo, expected):
    state = dedent("""
        123
        456
        789
    """)[1:-1]
    assert Board.rotate(state, direction, undo=undo) == expected


@pytest.mark.parametrize('direction, undo', [
    ('UP', False), ('RIGHT', False), ('DOWN', False), ('LEFT', False),
    ('UP', True), ('RIGHT', True), ('DOWN', True), ('LEFT', True),
])
def test_board_rotate_with_symbols(direction, undo):
    state = dedent("""
        -^-
        <->
        -v-
    """)[1:-1]

    assert Board.rotate(state, direction, undo=undo) == state


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
def test_board_rotate_rectangle(direction, expected):
    state = dedent("""
        abcd
        efgh
        ijkl
    """)[1:-1]

    assert Board.rotate(state, direction) == expected


# Bot.ini
# ============================================================================
def test_bot_initializes_with_position_and_uid(board1):
    bot_coord = Coord(2, 2)
    bot = Bot(board1, position=bot_coord, uid='m')

    assert bot.board is board1
    assert bot.uid is 'm'
    assert bot.cell == Cell(2, 2, 'm')


def test_bot_initializes_with_defaults_1(board1):
    bot = Bot(board1)

    assert bot.uid is 'b'
    assert bot.cell == Cell(2, 2, 'b')


def test_bot_initializes_with_defaults_2(board2):
    bot = Bot(board2)

    assert bot.uid is 'b'
    assert bot.cell == Cell(2, 5, 'b')


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
def test_bot_ping(board1):
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


def test_bot_find_path_returns_empty_list():
    grid = dedent("""
        #######
        #--#--#
        #--#-b#
        #--#--#
        #-----#
        #-----#
        #######
    """)[1:-1]

    board = Board.from_str(grid)
    bot = Bot(board)
    assert bot.find_path('e') == []


# Bot.find_position
# ============================================================================
@pytest.mark.parametrize('state, expected', [
    [
        dedent("""
            2
            #--
            #b-
            #--
        """)[1:-1],
        dedent("""
            #######
            #--#--#
            #^v#^v#
            #--#-v#
            e----v#
            #-<<<-#
            #######
        """)[1:-1]
    ],
    [
        dedent("""
            2
            #--
            #b-
            #--
            #--
        """)[1:-1],
        dedent("""
            #######
            #--#--#
            #--#--#
            #--#-v#
            e----v#
            #-<<--#
            #######
        """)[1:-1]
    ],
    [
        dedent("""
            2
            #--oo
            #--oo
            #--##
            #--b-
            #----
        """)[1:-1],
        dedent("""
            #######
            #--#--#
            #--#--#
            #--#<-#
            e-----#
            #-----#
            #######
        """)[1:-1]
    ],
    [
        dedent("""
            2
            ####
            #--#
            #--#
            #b-#
            ---o
            ---o
        """)[1:-1],
        dedent("""
            #######
            #--#--#
            #--#--#
            #--#^-#
            e-----#
            #-----#
            #######
        """)[1:-1]
    ],
    [
        dedent("""
            2
            ---ooo
            -b####
            -----#
            -----#
            oo####
        """)[1:-1],
        dedent("""
            #######
            #--#--#
            #--#--#
            #--#--#
            e--<--#
            #-----#
            #######
        """)[1:-1]
    ],
])
def test_bot_find_position(state, expected):
    master = dedent("""
        #######
        #--#--#
        #--#--#
        #--#--#
        e-----#
        #-----#
        #######
    """)[1:-1]
    board = Board.from_input(state)
    bot = Bot(board)

    positions = bot.find_position(master)

    assert str(positions) == expected


# Bot.simulate_move
# ============================================================================
@pytest.mark.parametrize('coord, direction, expected', [
    [
        Coord(5, 3),
        'LEFT',
        dedent("""
            #--
            #b-
            #--
        """)[1:-1]
    ],
    [
        Coord(5, 3),
        'RIGHT',
        dedent("""
            --#
            -b#
            --#
        """)[1:-1]
    ],
    [
        Coord(5, 3),
        'DOWN',
        None
    ],
    [
        Coord(5, 3),
        'UP',
        dedent("""
            -#-
            -b-
            ---
        """)[1:-1]
    ],
])
def test_bot_simulate_move(coord, direction, expected):
    master = dedent("""
        #######
        #--#--#
        #--#--#
        #--#--#
        e-----#
        #-----#
        #######
    """)[1:-1]
    board = Board.from_str(master)

    assert Bot.simulate_move(board, coord, direction) == expected


# Bot.simulate_all_moves
# ============================================================================
def test_bot_simulate_all_moves():
    master = dedent("""
        #######
        #--#--#
        #--#--#
        #--#--#
        e-----#
        #-----#
        #######
    """)[1:-1]
    positions = dedent("""
        #######
        #--#--#
        #^v#^v#
        #--#-v#
        e----v#
        #-<<<-#
        #######
    """)[1:-1]

    expected = {
        'DOWN': {'--#\n-b#\n--#', '###\n-b#\n--#', '--e\n-b#\n--#', '---\n-b#\n--#'},
        'RIGHT': {'###\n-b-\n---', '#--\n-b-\n---', '-##\n-b-\n---', '-#-\n-b-\n---', '--#\n-b-\n---'},
        'UP': {'###\n#b-\n#--', '---\n#b-\n#--', '#--\n#b-\n#--', '##e\n#b-\n#--'}
    }

    assert Bot.simulate_all_moves(positions, master) == expected


# Bot.simulate_all_moves
# ============================================================================
def test_bot_reveal_map():
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
        #b-
        #--
    """)[1:-1]
    moves = {
        'DOWN': {'--#\n-b#\n--#', '###\n-b#\n--#', '--e\n-b#\n--#', '---\n-b#\n--#'},
        'RIGHT': {'###\n-b-\n---', '#--\n-b-\n---', '-##\n-b-\n---', '-#-\n-b-\n---', '--#\n-b-\n---'},
        'UP': {'###\n#b-\n#--', '---\n#b-\n#--', '#--\n#b-\n#--', '##e\n#b-\n#--'}
    }
    board = Board.from_input(state)
    bot = Bot(board)

    assert bot.reveal_map(moves, master) == ['RIGHT', 'UP', 'DOWN']


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


# Cartesian.hash
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


# Other
# ============================================================================
def test_bot_next_move_1():
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


def test_bot_next_move_2():
    master = dedent("""
#######
#--#--#
#--#1-#
#--#-2#
e-----#
#-----#
#######
    """)[1:-1]
    state = dedent("""
        2
        o---
        o-b-
        #--#
        #--#
        #--#
        ####
    """)[1:-1]
    data = dedent("""
        1
        ---
        -b-
        --#
    """)[1:-1]
    board = Board.from_input(state)
    board.merge(Board.from_input(data))
    bot = Bot(board)

    assert bot.next_move(master) == 'RIGHT'
