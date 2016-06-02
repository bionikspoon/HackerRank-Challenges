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
        targets = sorted(((target, self.get_proximity(target)) for target in targets), key=itemgetter(1))

        grid_size = self.board.grid_size - 1
        quadrant_size = grid_size // 2
        q1_box = Quadrant(0, quadrant_size, 0, quadrant_size)
        q2_box = Quadrant(0, quadrant_size, quadrant_size, grid_size)
        q3_box = Quadrant(quadrant_size, grid_size, quadrant_size, grid_size)
        q4_box = Quadrant(quadrant_size, grid_size, 0, quadrant_size)

        q1_targets = []
        q2_targets = []
        q3_targets = []
        q4_targets = []

        for q_box, q_targets in (
        (q1_box, q1_targets), (q2_box, q2_targets), (q3_box, q3_targets), (q4_box, q4_targets)):
            for target, distance in targets:
                print(target.y, q_box.y_start, q_box.y_end)
                if target.y < q_box.y_start or target.y > q_box.y_end:
                    continue
                if target.x < q_box.x_start or target.x > q_box.x_end:
                    continue
                q_targets.append((target, distance))

        prioritized_targets = []

        if not q1_targets:
            prioritized_targets.extend(q2_targets)
            prioritized_targets.extend(q4_targets)
        if not q2_targets:
            prioritized_targets.extend(q3_targets)
            prioritized_targets.extend(q1_targets)
        if not q3_targets:
            prioritized_targets.extend(q4_targets)
            prioritized_targets.extend(q2_targets)
        if not q4_targets:
            prioritized_targets.extend(q1_targets)
            prioritized_targets.extend(q3_targets)

        if all((q1_targets, q2_targets, q3_targets, q4_targets)):
            prioritized_targets.extend(targets)

        prioritized_targets = sorted(tuple(set(prioritized_targets)), key=itemgetter(1))

        print('q1_targets', q1_targets)
        print('q2_targets', q2_targets)
        print('q3_targets', q3_targets)
        print('q4_targets', q4_targets)
        print('prioritized_targets', prioritized_targets)
        return targets[0][0]

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
    grid_size = len(grid)
    board = Board(grid_size, grid)
    bot = Bot(board, 'b')

    if not board.find('b'):
        return print('CLEAN')

    board.set_cell(Coord(posr, posc), 'b')

    move = bot.suggest_move('d')

    return print(MOVE_DES[move])


def parse_input(grid):
    bot_pos = Coord(*map(int, grid.pop(0).split()))
    grid_size = len(grid)
    return bot_pos, grid_size, '\n'.join(grid)


def main():
    bot_pos, grid_size, grid = parse_input([line.strip() for line in input()])
    next_move(bot_pos.y, bot_pos.x, grid)


if __name__ == '__main__':
    main()
