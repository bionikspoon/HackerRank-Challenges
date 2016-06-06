# coding=utf-8
from copy import deepcopy
from itertools import chain
from operator import eq
from pprint import pprint

import sys

RAISE = 'RAISE'


class Board(object):
    _state = []

    def __init__(self, state, dimensions):
        """
        :param str state:
        :param Dimensions dimensions:
        """
        self.dimensions = dimensions

        if isinstance(state, list):
            self._state = state
        if isinstance(state, str):
            self.state = state

    @classmethod
    def from_str(cls, data):
        """
        :param str data:
        :rtype: Board
        """
        lines = data.split('\n')
        dimensions = Dimensions(len(lines), len(lines[0]))
        return cls(data, dimensions)

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, value):
        """
        :param str value:
        """
        self._state = [[Cell(y, x, char) for x, char in enumerate(row)]
                       for y, row in enumerate(value.split('\n')) if row]

    def __iter__(self):
        return (cell for row in self.state for cell in row)

    def iter_box(self, min_y, min_x, dimensions):
        max_y, max_x = dimensions.y + min_y, dimensions.x + min_x
        for y, row in enumerate(self.state):
            if y < min_y or y > max_y:
                continue

            for x, cell in enumerate(row):
                if x < min_x or x > max_x:
                    continue
                yield cell

    def find(self, target, default=RAISE):
        """
        :param str|Coord target:
        :param any default:
        :return: Target Cell
        :rtype: Cell
        :raises InvalidTarget:
        """
        if hasattr(target, 'x') and hasattr(target, 'y') and not self.is_valid(target):
            raise InvalidTarget('Target is not valid')

        if isinstance(target, Coord):
            return self.state[target.y][target.x]

        for cell in self:
            if cell.value == target:
                return cell

        if default is not RAISE:
            return default

        raise InvalidTarget('Target not found')

    def filter(self, value, cmp=eq):
        """
        Filter cells.

        :param str value:
        :param cmp:
        """
        return (cell for cell in self if cmp(cell.value, value))

    def set(self, target, value):
        """
        Set target cell value.

        :param Coord target:
        :param str value:
        :raises InvalidTarget:
        """
        if not self.is_valid(target):
            raise InvalidTarget('Target is not valid')

        target_cell = self.find(target)
        target_cell.value = value

    def is_valid(self, target):
        """
        :param Coord target:
        :return: Target is valid
        :rtype: bool
        """
        if not isinstance(target, Coord):
            return False

        if target.x < 0 or target.x >= self.dimensions.x:
            return False
        if target.y < 0 or target.y >= self.dimensions.y:
            return False

        return True

    def fork(self):
        """
        :return: A selectively deep copy board copy
        :rtype: Board
        """
        # noinspection PyPep8Naming
        BoardClass = self.__class__
        state = deepcopy(self.state)
        return BoardClass(state, self.dimensions)

    def move(self, start, end, trail='-'):
        """
        :param Coord|str start:
        :param Delta|Coord end:
        :param str trail:
        :raises InvalidTarget:
        """

        start_cell = self.find(start)
        end_cell = self.find(end.resolve(start_cell) if isinstance(end, Delta) else end)

        if end_cell.value is '#':
            raise InvalidTarget('Cannot move into #')

        self.set(end_cell, start_cell.value)
        self.set(start_cell, trail)

    @staticmethod
    def to_string(state):
        """
        Convert state to string.

        :param [list] state:
        :rtype: str
        """
        return '\n'.join(''.join(cell.value if hasattr(cell, 'value') else cell for cell in row) for row in state)

    def __str__(self):
        return self.to_string(self.state)


class PartialBoard(Board):
    def __init__(self, state, dimensions, bot_position=None):
        """
        :param str state:
        :param Dimensions dimensions:
        :param Coord bot_position:
        """
        super(PartialBoard, self).__init__(state, dimensions)
        if bot_position:
            self.set(bot_position, 'b')

    @classmethod
    def from_str(cls, data):
        """
        Create a PartialBoard from input

        :param str data:
        :rtype: PartialBoard
        """
        data = data.strip().split('\n')
        direction = None
        if data[0] in ('UP', 'DOWN', 'RIGHT', 'LEFT'):
            direction = data.pop(0)

        _ = data.pop(0)

        dimensions = Dimensions(y=len(data), x=len(data[0]))
        state = cls.to_string(data)

        return cls.with_move(state, dimensions, direction=direction)

    @classmethod
    def with_move(cls, state, dimensions, direction=None):
        """
        Create a PartialBoard with initial move.

        :param str state:
        :param Dimensions dimensions:
        :param str direction:
        :rtype: PartialBoard
        """
        if direction is None:
            return cls(state, dimensions, bot_position=Coord(1, 1))
        state = cls.rotate(state, direction)

        self = cls(state, dimensions)
        self.dimensions.y, self.dimensions.x = len(self.state), len(self.state[0])

        self.move('b', MOVE['UP'])

        return self

    @staticmethod
    def rotate(state, direction):
        """
        :param str state:
        :param str direction:
        :return: Rotated state
        :rtype: str
        """
        state = [list(line) for line in state.split('\n')]
        next_state = None

        if direction == 'UP':
            next_state = state
        if direction == 'RIGHT':
            next_state = reversed(list(zip(*state)))
        if direction == 'DOWN':
            next_state = [reversed(args) for args in reversed(state)]
        if direction == 'LEFT':
            next_state = [reversed(args) for args in zip(*state)]

        if next_state is None:
            raise InvalidTarget('Direction not in UP RIGHT DOWN LEFT')

        return '\n'.join(''.join(line) for line in next_state)

    def merge(self, other, target='b'):
        self_target = self.find(target)
        other_target = other.find(target)

        self_padding = {
            'UP': self_target.y,
            'DOWN': self.dimensions.y - self_target.y,
            'LEFT': self_target.x,
            'RIGHT': self.dimensions.x - self_target.x,
        }
        other_padding = {
            'UP': other_target.y,
            'DOWN': other.dimensions.y - other_target.y,
            'LEFT': other_target.x,
            'RIGHT': other.dimensions.x - other_target.x,
        }
        padding = {key: value - other_padding[key] for key, value in self_padding.items()}
        padding = [[key] * abs(value) for key, value in padding.items() if value < 0]
        padding = [direction for directions in padding for direction in directions]
        self.pad(padding)

        box = self.iter_box(
            self_target.y - other_target.y,
            self_target.x - other_target.x,
            other.dimensions
        )
        for self_cell, other_cell in zip(box, other):
            if self_cell.value == 'o':
                self_cell.value = other_cell.value
            print(self_cell, other_cell)

    def pad(self, directions):
        if not directions:
            for y, row in enumerate(self.state):
                for x, cell in enumerate(row):
                    cell.y, cell.x = y, x
            return

        direction = directions.pop()

        if 'LEFT' is direction:
            self.dimensions.x += 1
            for row in self.state:
                row.insert(0, Cell(0, 0, 'o'))
        if 'RIGHT' is direction:
            self.dimensions.x += 1
            for row in self.state:
                row.append(Cell(0, 0, 'o'))
        if 'UP' is direction:
            self.dimensions.y += 1
            self.state.insert(0, [Cell(0, 0, 'o') for _ in range(self.dimensions.x)])
        if 'DOWN' is direction:
            self.dimensions.y += 1
            self.state.append([Cell(0, 0, 'o') for _ in range(self.dimensions.x)])

        self.pad(directions)


class Bot(object):
    def __init__(self, board, position=None, registry=None, uid='b'):
        """
        :param Board board:
        :param Coord position:
        :param dict registry:
        :param str uid:
        """
        self.board = board
        self.uid = uid
        self.registry = {} if registry is None else registry

        if position:
            self.board.set(position, self.uid)

        self.registry[self.cell.to_coord()] = self

    @property
    def cell(self):
        """
        :return: Bot position
        :rtype: Cell
        """
        return self.board.find(self.uid)

    def move(self, target):
        """
        :param str|Delta|Coord target:
        """
        target = MOVE[target] if isinstance(target, str) else target

        self.board.move(self.cell, target)

    def fork(self, direction, board=None):
        """
        :param str direction:
        :param Board board:
        :return: A forked bot
        :rtype: Bot
        """
        # noinspection PyPep8Naming
        BotClass = self.__class__
        board = board or self.board
        cell = self.cell
        uid = ' '.join((self.cell.value, direction))
        target = board.find(MOVE[direction].resolve(cell), None)

        if not target or target.value not in 'e-':
            return None

        board.set(target, uid)

        return BotClass(board, uid=uid, registry=self.registry)

    def ping(self):
        """Fork in every direction"""
        directions = ('UP', 'RIGHT', 'DOWN', 'LEFT')

        return (bot for bot in (self.fork(direction) for direction in directions) if bot)

    def find_position(self, master):
        board = self.board
        matches = []
        for cell in master.filter('-'):
            box_y, box_x = cell.y - 1, cell.x - 1
            for board_cell, master_cell in zip(board, master.iter_box(box_y, box_x, board.dimensions)):
                if board_cell.value in 'bo':
                    continue

                if board_cell.value != master_cell.value:
                    print(board_cell, master_cell)
                    break

                # print(board_cell, master_cell)
            else:
                matches.append(cell)
        print(matches)

    def find_path(self, target):
        """
        Fork bot in every direction until fastest path to target is found

        :param str|Coord target:
        :return: Path to target
        :rtype: [str]
        """
        # noinspection PyPep8Naming
        BotClass = self.__class__
        board = self.board.fork()
        registry = {}
        bot = BotClass(board, registry=registry, uid=self.uid)
        target = board.find(target).to_coord()

        bots = tuple(bot.ping())
        while not registry.get(target):
            bots = tuple(chain.from_iterable((bot.ping() for bot in bots)))

        path_finder = registry.get(target)
        return path_finder.uid.split(' ')[1:]

    def next_move(self):
        """Get next move"""
        return self.find_path('e')[0]

    def __repr__(self):
        return '{0.__class__.__name__}(y={0.cell.y}, x={0.cell.x}, uid={0.uid!r})'.format(self)


class Cartesian(object):
    def __init__(self, y, x):
        """
        :param int y:
        :param int x:
        """
        self.y = y
        self.x = x

    def __repr__(self):
        return '{0.__class__.__name__}(y={0.y}, x={0.x})'.format(self)

    def __eq__(self, other):
        return self.y == other.y and self.x == other.x

    def __hash__(self):
        return hash((self.y, self.x))


class Coord(Cartesian):
    def to_cell(self, value):
        """
        :param str value:
        :rtype: Cell
        """
        return Cell(self.y, self.x, value)

    def to_coord(self):
        """
        :rtype: Coord
        """
        return Coord(self.y, self.x)

    def to_delta(self, dest):
        """
        :param Delta|Coord dest:
        :rtype: Delta
        """
        if isinstance(dest, Delta):
            return dest

        y = dest.y - self.y
        x = dest.x - self.x

        return Delta(y, x)

    def get_distance(self, dest):
        """
        :param Delta|Coord dest:
        :rtype: int
        """
        delta = self.to_delta(dest)
        return abs(delta.y) + abs(delta.x)


class Cell(Coord):
    def __init__(self, y, x, value):
        """
        :param int y:
        :param int x:
        :param str value:
        """
        super(Cell, self).__init__(y, x)
        self.value = value

    def to_cell(self, value=None):
        """
        :param str|None value:
        :rtype: Cell
        """
        self.value = value or self.value
        return self

    def __repr__(self):
        return '{0.__class__.__name__}({0.y}, {0.x}, {0.value!r})'.format(self)

    def __eq__(self, other):
        return super(Cell, self).__eq__(other) and self.value == other.value


class Delta(Cartesian):
    def resolve(self, start):
        """
        :param Coord start:
        :return: Coord relative to start
        :rtype: Coord
        """
        y = start.y + self.y
        x = start.x + self.x
        return Coord(y, x)


class Dimensions(Cartesian):
    pass


class InvalidTarget(Exception):
    pass


MOVE = {
    'LEFT': Delta(0, -1),
    'RIGHT': Delta(0, 1),
    'UP': Delta(-1, 0),
    'DOWN': Delta(1, 0),
}


def parse_input(data):
    data = data.strip().split('\n')
    if data[0] in ('UP', 'DOWN', 'RIGHT', 'LEFT'):
        direction = data.pop(0)
        _ = data.pop(0)

        state = list(map(list, rotate(data, direction)))
        print(state)

        y, x = [(y, x) for y, row in enumerate(state) for x, cell in enumerate(row) if cell == 'b'][0]
        state[y][x] = '-'
        state[y - 1][x] = 'b'
    else:
        _ = data.pop(0)
        state = [list(row) for row in data]
    return state


def combine_input(prev_state, next_state):
    prev_state = parse_input(prev_state)
    next_state = parse_input(next_state)

    dim_y, dim_x = len(prev_state), len(prev_state[0])
    bot = Coord(0, 0)
    for y, row in enumerate(prev_state):
        for x, cell in enumerate(row):
            if cell == 'b':
                bot = Coord(y, x)

    if bot.y == 0:
        dim_y += 1
        bot.y += 1
        prev_state.insert(0, ['o' for _ in range(dim_x)])
    if bot.y == dim_y - 1:
        dim_y += 1
        prev_state.append(['o' for _ in range(dim_x)])
        pass
    if bot.x == 0:
        dim_x += 1
        bot.x += 1

        for row in prev_state:
            row.insert(0, 'o')
    if bot.x == dim_x - 1:
        dim_x += 1
        for row in prev_state:
            row.append('o')

    for y, row in enumerate(next_state):
        for x, next_cell in enumerate(row):
            rel = Delta(y - 1, x - 1)
            prev_cell = prev_state[bot.y + rel.y][bot.x + rel.x]
            if prev_cell != 'o':
                continue
            prev_state[bot.y + rel.y][bot.x + rel.x] = next_cell

    # state = [next_state.pop()] + prev_state

    return '\n'.join(''.join(line) for line in prev_state)


def rotate(data, direction):
    if direction == 'UP':
        return data
    if direction == 'RIGHT':
        return reversed([list(args) for args in zip(*data)])
    if direction == 'DOWN':
        return [list(reversed(args)) for args in reversed(data)]
    if direction == 'LEFT':
        return [list(reversed(args)) for args in zip(*data)]


def main():
    data = sys.stdin.read().rstrip()
    board = Board.from_str(data)
    bot = Bot(board)
    print(bot.next_move())


if __name__ == '__main__':
    main()
