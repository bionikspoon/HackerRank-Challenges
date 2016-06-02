from collections import namedtuple
from fileinput import input

Coord = namedtuple('Coord', 'y x')
Delta = namedtuple('Delta', 'y x')
Cell = namedtuple('Cell', 'y x value')

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
    def __init__(self, board=None):
        self.board = board

    def suggest_move(self, char, target, op='+'):
        char_cell, target_cell = self.board.find(char), self.board.find(target)
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


def parse_input(grid):
    grid_size = int(grid.pop(0))
    return grid_size, '\n'.join(grid)


def main():
    grid_size, grid = parse_input([line.strip() for line in input()])
    board = Board(grid_size, grid)
    bot = Bot(board)
    while True:
        move = bot.suggest_move('m', 'p')
        board.move('m', move)

        print(MOVE_DES[move])

        if not board.find('p'):
            break


if __name__ == '__main__':
    main()
