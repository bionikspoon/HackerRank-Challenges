# coding=utf-8
from __future__ import print_function

import os
import sys
from collections import namedtuple
from fileinput import input
from fractions import Fraction
from itertools import product
from operator import itemgetter, attrgetter
from pprint import pformat

Coord = namedtuple('Coord', 'y x')
Delta = namedtuple('Delta', 'y x')
Cell = namedtuple('Cell', 'y x value')
Dimensions = namedtuple('Dimensions', 'y x')

MOVE_LEFT = Delta(0, -1)
MOVE_RIGHT = Delta(0, 1)
MOVE_UP = Delta(-1, 0)
MOVE_DOWN = Delta(1, 0)

MOVE_DES = {
    MOVE_DOWN: 'DOWN',
    MOVE_LEFT: 'LEFT',
    MOVE_UP: 'UP',
    MOVE_RIGHT: 'RIGHT',
}


class Board(object):
    _state = None

    def __init__(self, dimensions, state):
        self.dimensions = dimensions
        self.state = state

        y_min, x_min = 0, 0
        y_max, x_max = dimensions.y, dimensions.x
        y_mid = y_max // 2
        x_mid = x_max // 2

        self.quadrants = {
            1: (tuple(range(y_min, y_mid)), tuple(range(x_min, x_mid))),
            2: (tuple(range(y_min, y_mid)), tuple(range(x_mid, x_max))),
            3: (tuple(range(y_mid, y_max)), tuple(range(x_mid, x_max))),
            4: (tuple(range(y_mid, y_max)), tuple(range(x_min, x_mid))),
        }
        self.corners = (
            self.find(Coord(y_min, x_min)),
            self.find(Coord(y_min, x_max - 1)),
            self.find(Coord(y_max - 1, x_max - 1)),
            self.find(Coord(y_max - 1, x_min)),
        )

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, value):
        self._state = [[Cell(y, x, char) for x, char in enumerate(row)] for y, row in enumerate(value.split('\n')) if
                       row]

    def iter_cells(self):
        return (cell for row in self.state for cell in row)

    def iter_cells_by_quadrant(self, quadrant):
        quadrant_coords = self.quadrants[quadrant]
        return (self.state[y][x] for y, x in product(*quadrant_coords))

    def find(self, target):
        if hasattr(target, 'x') and hasattr(target, 'y') and not self.is_valid_coord(target):
            raise InvalidMove()

        if isinstance(target, Cell):
            return target

        if isinstance(target, Coord):
            return self.state[target.y][target.x]

        for cell in self.iter_cells():
            if cell.value == target:
                return cell

        return None

    def findall(self, value):
        return [cell for cell in self.iter_cells() if cell.value == value]

    def findall_in_quadrant(self, quadrant, value):
        return [cell for cell in self.iter_cells_by_quadrant(quadrant) if cell.value == value]

    def set_cell(self, target, value):
        if not self.is_valid_coord(target):
            raise InvalidMove()

        target_cell = self.find(target)
        self.state[target_cell.y][target_cell.x] = Cell(target_cell.y, target_cell.x, value)

    def is_valid_coord(self, coord):
        if not isinstance(coord, (Coord, Cell)):
            return False

        if coord.x < 0 or coord.x >= self.dimensions.x:
            return False
        if coord.y < 0 or coord.y >= self.dimensions.y:
            return False

        return True

    def move(self, a, b, trail='-'):
        cell_a = self.find(a)
        cell_b = self.find(utils.resolve_delta(a, b))

        self.set_cell(cell_a, trail)
        self.set_cell(cell_b, cell_a.value)

    def pformat(self):
        return '\n'.join(''.join(cell.value for cell in row) for row in self.state)


# noinspection PyMethodMayBeStatic
class Bot(object):
    def __init__(self, board, position=None, char='b'):
        self.board = board
        self.char = char

        self.position = self.board.find(position) or self.cell

        self.track = [self.board.find(coord) for coord in [
            Coord(1, 1), Coord(1, 2), Coord(1, 3), Coord(2, 3), Coord(3, 3), Coord(3, 2), Coord(3, 1), Coord(2, 1)
        ]]

    @property
    def cell(self):
        return self.board.find(self.char)

    def prefer_proximity(self, target):
        denominator = utils.find_distance(self.cell, target)
        return Fraction(100, denominator)

    def prefer_current_quadrant(self, bot_quadrant, target_quadrant):
        denominator = 1 if bot_quadrant == target_quadrant else 2
        return Fraction(100, denominator)

    def prefer_traverse_adjacent_quadrant(self, cleared_quadrants, target_quadrant):
        quadrants = {
            1: 2,
            2: 2,
            3: 2,
            4: 2,
        }
        if 1 in cleared_quadrants or 3 in cleared_quadrants:
            quadrants[2] = 1
            quadrants[4] = 1

        if 2 in cleared_quadrants or 4 in cleared_quadrants:
            quadrants[1] = 1
            quadrants[3] = 1

        denominator = quadrants[target_quadrant]
        return Fraction(100, denominator)

    def prefer_corners(self, target, corners):
        denominator = 1 if target in corners else 2
        return Fraction(100, denominator)

    def prefer_get_on_track(self, target, track_cells):
        bot_cell = self.cell
        if bot_cell in track_cells:
            return 0

        if target not in track_cells:
            return 0

        track_cells = [(track_cell, utils.find_distance(bot_cell, track_cell)) for track_cell in track_cells]
        track_cells = sorted(track_cells, key=itemgetter(1))

        for i, (track_cell, distance) in enumerate(track_cells):
            if target == track_cell:
                denominator = i + 1
                return Fraction(100, denominator)

    def prefer_stay_on_track(self, target, track_cells):
        if self.cell not in track_cells:
            return 0
        index = track_cells.index(self.cell)
        next_index = index + 1 if index + 1 < len(track_cells) else 0
        denominator = 1 if track_cells[next_index] == target else 2
        return Fraction(100, denominator)

    def choose_target(self, targets, **kwargs):
        kwargs.setdefault('proximity', 8)
        kwargs.setdefault('current_quadrant', 8)
        kwargs.setdefault('traverse_adjacent_quadrant', 8)
        kwargs.setdefault('corners', 1)
        kwargs.setdefault('on_track', 0)

        target_char = targets[0].value
        bot_quadrant = utils.find_cell_quadrant(self.board, self.cell)
        target_list = []
        cleared_quadrants = [quadrant for quadrant in range(1, 5) if
                             not list(self.board.findall_in_quadrant(quadrant, target_char))]
        for cell in targets:
            preferences = {}
            target = {'cell': cell, 'preferences': preferences}
            target_quadrant = utils.find_cell_quadrant(self.board, cell)

            preferences['proximity'] = Preference(
                'proximity',
                self.prefer_proximity(cell),
                kwargs
            )

            preferences['current_quadrant'] = Preference(
                'current_quadrant',
                self.prefer_current_quadrant(bot_quadrant, target_quadrant),
                kwargs
            )

            preferences['traverse_adjacent_quadrant'] = Preference(
                'traverse_adjacent_quadrant',
                self.prefer_traverse_adjacent_quadrant(cleared_quadrants, target_quadrant),
                kwargs
            )

            preferences['corners'] = Preference(
                'corners',
                self.prefer_corners(cell, self.board.corners),
                kwargs
            )

            preferences['get_on_track'] = Preference(
                'get_on_track',
                self.prefer_get_on_track(cell, self.track),
                kwargs['on_track']
            )

            preferences['stay_on_track'] = Preference(
                'stay_on_track',
                self.prefer_stay_on_track(cell, self.track),
                kwargs['on_track']
            )

            target['priority'] = sum(preferences.values())
            target_list.append(target)

        target_list = sorted(target_list, key=itemgetter('priority'), reverse=True)
        debug_preferences(target_list)
        return target_list[0]['cell']

    def suggest_move(self, target, **kwargs):
        bot_cell = self.cell
        target_cells = self.board.findall(target)

        if not target_cells:
            return None

        target_cell = self.choose_target(target_cells, **kwargs)
        delta = utils.find_delta(bot_cell, target_cell)

        track_coords = (Coord(y=cell.y, x=cell.x) for cell in self.track)

        if delta.x > 0 and utils.resolve_delta(bot_cell, MOVE_RIGHT) in track_coords:
            return MOVE_RIGHT
        if delta.x < 0 and utils.resolve_delta(bot_cell, MOVE_LEFT) in track_coords:
            return MOVE_LEFT
        if delta.y > 0 and utils.resolve_delta(bot_cell, MOVE_DOWN) in track_coords:
            return MOVE_DOWN
        if delta.y < 0 and utils.resolve_delta(bot_cell, MOVE_UP) in track_coords:
            return MOVE_UP

        if delta.x > 0:
            return MOVE_RIGHT
        if delta.x < 0:
            return MOVE_LEFT
        if delta.y > 0:
            return MOVE_DOWN
        if delta.y < 0:
            return MOVE_UP

        raise NoValidMove()


class Preference(object):
    def __init__(self, name, score, weight):
        self.name = name
        self.score = score
        self.weight = weight[name] if isinstance(weight, dict) else weight

    @property
    def product(self):
        return int(self.score * self.weight)

    def __radd__(self, other):
        return self.product + (other.product if isinstance(other, self.__class__) else other)

    def __repr__(self):
        return '{0.__class__.__name__[0]} {0.product:>6} {0.name}'.format(self)


class InvalidMove(Exception):
    pass


class NoValidMove(Exception):
    pass


# noinspection PyPep8Naming
class utils(object):
    @staticmethod
    def find_delta(start, finish):
        if start is None or finish is None:
            raise NoValidMove()

        delta_y = finish.y - start.y
        delta_x = finish.x - start.x
        return Delta(delta_y, delta_x)

    @staticmethod
    def resolve_delta(start, delta):
        if isinstance(delta, (Coord, Cell)):
            return delta

        if not isinstance(delta, Delta):
            raise TypeError()

        coord = Coord(start.y + delta.y, start.x + delta.x)
        return coord

    @staticmethod
    def find_distance(start, finish):
        delta = finish if isinstance(finish, Delta) else utils.find_delta(start, finish)
        return abs(delta.x) + abs(delta.y)

    @staticmethod
    def find_cell_quadrant(board, cell):
        for name, (quad_y, quad_x) in board.quadrants.items():
            if cell.y not in quad_y or cell.x not in quad_x:
                continue
            return name
        return None

    @staticmethod
    def is_debug():
        return os.environ.get('PY_TEST') == 'DEBUG'


def debug(*args, **kwargs):
    kwargs.setdefault('file', sys.stderr)

    if kwargs.pop('pformat', True):
        print(*map(pformat, args), **kwargs)
    else:
        print(*args, **kwargs)


def debug_preferences(targets):
    targets = reversed(targets) if utils.is_debug() else targets
    for target in targets:
        debug('\n{0[priority]:>9} {0[cell]}'.format(target), pformat=False)
        debug(tuple(
            preference
            for preference
            in sorted(target['preferences'].values(), key=attrgetter('product'), reverse=True)
        ))


def bot_factory(pos_y, pos_x, grid):
    position = Coord(pos_y, pos_x)
    grid_size = len(grid.split('\n'))
    dimensions = Dimensions(grid_size, grid_size)
    board = Board(dimensions, grid)
    bot = Bot(board, position)

    return board, bot


def parse_input(data):
    position, grid = data.split('\n', 1)
    pos_y, pos_x = map(int, position.split())
    return pos_y, pos_x, grid


def next_move(pos_y, pos_x, grid):
    board, bot = bot_factory(pos_y, pos_x, grid)

    if bot.position.value == 'd':
        return 'CLEAN'

    move = bot.suggest_move('d')
    if not move:
        move = bot.suggest_move('o', on_track=2)

    return MOVE_DES[move]


def get_prev_state(filename):
    if not os.path.isfile(filename):
        return None

    with open(filename) as f:
        return ''.join(f.readlines())


def set_next_state(filename, state):
    with open(filename, 'w') as f:
        f.write(state)


def merge_state(prev_state, next_state):
    return ''.join(p if n == 'o' else n for p, n in zip(prev_state, next_state))


def main():
    data = '\n'.join(line.strip() for line in input())

    filename = 'moves.txt'
    prev_state = get_prev_state(filename)
    next_state = merge_state(prev_state, data) if prev_state else data
    set_next_state(filename, next_state)

    debug(next_state, pformat=False)

    pos_y, pos_x, grid = parse_input(next_state)
    print(next_move(pos_y, pos_x, grid))


if __name__ == '__main__':
    main()
