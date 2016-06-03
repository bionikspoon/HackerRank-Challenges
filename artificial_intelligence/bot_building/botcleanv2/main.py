# coding=utf-8
from __future__ import print_function
from collections import namedtuple
from fileinput import input
from operator import itemgetter

Coord = namedtuple('Coord', 'y x')
Delta = namedtuple('Delta', 'y x')
Cell = namedtuple('Cell', 'y x value')
Dimensions = namedtuple('Dimensions', 'y x')
Quadrant = namedtuple('Quadrant', 'y_start y_end x_start x_end')

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

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, value):
        self._state = [[Cell(y, x, char) for x, char in enumerate(row)] for y, row in enumerate(value.split('\n')) if
                       row]

    def iter_state(self):
        return (cell for row in self.state for cell in row)

    def find(self, target):
        if hasattr(target, 'x') and hasattr(target, 'y') and not self.is_valid_coord(target):
            raise InvalidMove()

        if isinstance(target, Cell):
            return target

        if isinstance(target, Coord):
            return self.state[target.y][target.x]

        for cell in self.iter_state():
            if cell.value == target:
                return cell

        return None

    def findall(self, value):
        return [cell for cell in self.iter_state() if cell.value == value]

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


class Bot(object):
    def __init__(self, board, position=None, char='b'):
        self.board = board
        self._char = char

        self.position = self.board.find(position) or self.char

    @property
    def char(self):
        return self.board.find(self._char)

    def get_proximity(self, target):
        char_cell = self.char
        target_cell = self.board.find(target)

        delta = utils.find_delta(char_cell, target_cell)
        return abs(delta.x) + abs(delta.y)

    def choose_target(self, targets):
        targets = [{'cell': target, 'proximity': self.get_proximity(target)} for target in targets]

        for target in targets:
            target['priority_inverse'] = target['proximity'] * 100
            target['quadrants'] = []
        dimensions = self.board.dimensions
        y_min, x_min = 0, 0
        y_max = dimensions.y - 1
        x_max = dimensions.x - 1
        y_mid = y_max // 2
        x_mid = x_max // 2
        quadrant_boxes = {
            'q1': Quadrant(y_min, y_mid, x_min, x_mid),
            'q2': Quadrant(y_min, y_mid, x_mid, x_max),
            'q3': Quadrant(y_mid, y_max, x_mid, x_max),
            'q4': Quadrant(y_mid, y_max, x_min, x_mid),
        }
        corner_coords = [Coord(y_min, x_min), Coord(y_min, x_max), Coord(y_max, x_max), Coord(y_max, x_min)]
        targets_by_quadrant = {
            'q1': [],
            'q2': [],
            'q3': [],
            'q4': [],
        }

        for quadrant_name, quadrant_box in quadrant_boxes.items():
            for target in targets:
                cell = target['cell']
                if cell.y < quadrant_box.y_start or cell.y > quadrant_box.y_end:
                    continue
                if cell.x < quadrant_box.x_start or cell.x > quadrant_box.x_end:
                    continue
                target['quadrants'].append(quadrant_name)
                targets_by_quadrant[quadrant_name].append(target)

        char_cell = self.char
        char_quadrants = []

        for quadrant_name, quadrant_box in quadrant_boxes.items():
            for target in [char_cell]:
                cell = target
                if cell.y < quadrant_box.y_start or cell.y > quadrant_box.y_end:
                    continue
                if cell.x < quadrant_box.x_start or cell.x > quadrant_box.x_end:
                    continue

                char_quadrants.append(quadrant_name)

        for target in targets:
            quadrant_priority = 1
            quadrant_coefficient = 10
            matching_coefficient = 1
            corner_coefficient = 1

            if not targets_by_quadrant['q1']:
                if 'q2' in target['quadrants'] or 'q4' in target['quadrants']:
                    quadrant_priority = quadrant_coefficient
            if not targets_by_quadrant['q2']:
                if 'q3' in target['quadrants'] or 'q1' in target['quadrants']:
                    quadrant_priority = quadrant_coefficient
            if not targets_by_quadrant['q3']:
                if 'q4' in target['quadrants'] or 'q2' in target['quadrants']:
                    quadrant_priority = quadrant_coefficient
            if not targets_by_quadrant['q4']:
                if 'q1' in target['quadrants'] or 'q3' in target['quadrants']:
                    quadrant_priority = quadrant_coefficient

            matching_quadrants = 0
            for target_quadrant in target['quadrants']:
                if target_quadrant in char_quadrants:
                    matching_quadrants += 1

            corner_modifier = 0

            target_coord = Coord(target['cell'].x, target['cell'].y)
            if target_coord in corner_coords:
                corner_modifier = 1 * corner_coefficient

            matching_quadrant_priority_multiplier = matching_quadrants * matching_coefficient + 1
            target['matching_quadrant_priority_multiplier'] = matching_quadrant_priority_multiplier

            quadrant_priority_multiplier = int(quadrant_priority / len(target['quadrants']))
            target['quadrant_priority_multiplier'] = quadrant_priority_multiplier

            target['corner_modifier'] = corner_modifier

            target['priority_inverse'] //= (quadrant_priority_multiplier + matching_quadrant_priority_multiplier)
            target['priority_inverse'] -= corner_modifier

        sorted_targets = sorted(targets, key=itemgetter('priority_inverse', 'proximity'))
        return sorted_targets[0]['cell']

    def suggest_move(self, target):
        char_cell = self.char
        target_cells = self.board.findall(target)

        if not target_cells:
            return None

        target_cell = self.choose_target(target_cells)
        delta = utils.find_delta(char_cell, target_cell)

        if delta.y > 0:
            return MOVE_DOWN
        if delta.y < 0:
            return MOVE_UP
        if delta.x > 0:
            return MOVE_RIGHT
        if delta.x < 0:
            return MOVE_LEFT

        raise NoValidMove()


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
    def setup(y, x, grid):
        position = Coord(y, x)
        grid_size = len(grid.split('\n'))
        dimensions = Dimensions(grid_size, grid_size)
        board = Board(dimensions, grid)
        bot = Bot(board, position)

        return board, bot

    @staticmethod
    def debug(*args, **kwargs):
        import sys

        kwargs.setdefault('file', sys.stderr)
        if kwargs.pop('pformat', None):
            from pprint import pformat

            print(*map(pformat, args))
        else:
            print(*args, **kwargs)


def parse_input(data):
    position, grid = data.split('\n', 1)
    y, x = map(int, position.split())
    return y, x, grid


def next_move(pos_y, pos_x, grid):
    board, bot = utils.setup(pos_y, pos_x, grid)

    if bot.position.value == 'd':
        return 'CLEAN'

    move = bot.suggest_move('d')
    if not move:
        move = bot.suggest_move('o')

    return MOVE_DES[move]


def main():
    y, x, grid = parse_input('\n'.join(line.strip() for line in input()))
    print(next_move(y, x, grid))


if __name__ == '__main__':
    main()
