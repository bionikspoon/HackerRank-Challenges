from __future__ import print_function
from collections import namedtuple
from fileinput import input
from operator import itemgetter

Coord = namedtuple('Coord', 'y x')
Delta = namedtuple('Delta', 'y x')
Cell = namedtuple('Cell', 'y x value')
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


def debug(*args, **kwargs):
    import sys

    kwargs.setdefault('file', sys.stderr)
    print(*args, **kwargs)


class Board(object):
    _state = None

    def __init__(self, grid_size, state):
        self.grid_size = grid_size
        self.state = state

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, value):
        self._state = [[char for char in line] for line in value.split('\n') if line]

    def iter_state(self):
        return (Cell(y, x, char) for y, row in enumerate(self.state) for x, char in enumerate(row))

    def find(self, needle):
        if isinstance(needle, Cell):
            return needle

        if isinstance(needle, Coord):
            return Cell(needle.y, needle.x, self.state[needle.y][needle.x])

        for cell in self.iter_state():
            if cell.value == needle:
                return cell

        return None

    def findall(self, value):
        return [cell for cell in self.iter_state() if cell.value == value]

    def set_cell(self, needle, value):
        needle_cell = self.find(needle)
        self.state[needle_cell.y][needle_cell.x] = value

    def is_valid_coord(self, coord):
        if not isinstance(coord, Coord):
            return False

        for axis in (coord.x, coord.y):
            if axis < 0 or axis >= self.grid_size:
                return False
        return True

    def resolve_delta(self, delta, ref):
        if not isinstance(delta, Delta):
            return delta

        ref_cell = self.find(ref)

        coord = Coord(ref_cell.y + delta.y, ref_cell.x + delta.x)

        if not self.is_valid_coord(coord):
            raise InvalidMove()

        return coord

    def find_delta(self, char, target):
        char_cell, target_cell = self.find(char), self.find(target)

        if char_cell is None or target_cell is None:
            raise NoValidMove()

        delta_y = target_cell.y - char_cell.y
        delta_x = target_cell.x - char_cell.x
        return Delta(delta_y, delta_x)

    def move(self, a, b):
        cell_a = self.find(a)
        cell_b = self.find(self.resolve_delta(b, a))

        self.set_cell(cell_a, '-')
        self.set_cell(cell_b, cell_a.value)

    def pformat(self):
        return '\n'.join(''.join(row) for row in self.state if row)


class Bot(object):
    def __init__(self, board=None, char='b'):
        self.board = board
        self._char = char

    @property
    def char(self):
        return self.board.find(self._char)

    @char.setter
    def char(self, value):
        self._char = value

    def get_proximity(self, target):
        char_cell = self.char
        target_cell = self.board.find(target)

        delta = self.board.find_delta(char_cell, target_cell)
        return abs(delta.x) + abs(delta.y)

    def choose_target(self, targets):
        targets = [{'cell': target, 'proximity': self.get_proximity(target)} for target in targets]

        for target in targets:
            target['priority_inverse'] = target['proximity'] * 100
            target['quadrants'] = []
        grid_size = self.board.grid_size - 1
        quadrant_size = grid_size // 2
        quadrant_boxes = {
            'q1': Quadrant(0, quadrant_size, 0, quadrant_size),
            'q2': Quadrant(0, quadrant_size, quadrant_size, grid_size),
            'q3': Quadrant(quadrant_size, grid_size, quadrant_size, grid_size),
            'q4': Quadrant(quadrant_size, grid_size, 0, quadrant_size),
        }

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
            matching_coeffient = 1
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
            corner_coords = [Coord(0, 0), Coord(grid_size, 0), Coord(grid_size, grid_size), Coord(0, grid_size)]
            target_coord = Coord(target['cell'].x, target['cell'].y)
            if target_coord in corner_coords:
                corner_modifier = 1 * corner_coefficient

            matching_quadrant_priority_multiplier = matching_quadrants * matching_coeffient + 1
            target['matching_quadrant_priority_multiplier'] = matching_quadrant_priority_multiplier

            quadrant_priority_multiplier = int(quadrant_priority / len(target['quadrants']))
            target['quadrant_priority_multiplier'] = quadrant_priority_multiplier

            target['corner_modifer'] = corner_modifier

            target['priority_inverse'] //= (quadrant_priority_multiplier + matching_quadrant_priority_multiplier)
            target['priority_inverse'] -= corner_modifier

        sorted_targets = sorted(targets, key=itemgetter('priority_inverse', 'proximity'))
        return sorted_targets[0]['cell']

    def suggest_move(self, target, op='+'):
        char_cell = self.char
        target_cells = self.board.findall(target)

        target_cell = self.choose_target(target_cells)
        delta = self.board.find_delta(char_cell, target_cell)

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


def next_move(posr, posc, grid):
    grid_size = len(grid.split('\n') if isinstance(grid, str) else grid)
    board = Board(grid_size, grid)
    bot = Bot(board, 'b')

    if not board.find('b'):
        return 'CLEAN'

    board.set_cell(Coord(posr, posc), 'b')

    move = bot.suggest_move('d')

    return MOVE_DES[move]


def parse_input(grid):
    bot_pos = Coord(*map(int, grid.pop(0).split()))
    grid_size = len(grid.split('\n') if isinstance(grid, str) else grid)
    return bot_pos, grid_size, '\n'.join(grid)


def main():
    bot_pos, grid_size, grid = parse_input([line.strip() for line in input()])
    print(next_move(bot_pos.y, bot_pos.x, grid))


if __name__ == '__main__':
    main()
