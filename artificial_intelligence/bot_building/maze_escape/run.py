# coding=utf-8
import json
import os.path
import shutil
import subprocess
import sys
from tempfile import TemporaryDirectory
from textwrap import dedent

EXECUTABLE = sys.executable  # python interpreter
TARGET = 'main.py'
REPLAY = 'moves.json'
BASE_PATH = os.path.abspath(os.path.dirname(__file__))


class Board(object):
    _state = []
    op = {
        'LEFT': lambda y, x: (y, x - 1),
        'RIGHT': lambda y, x: (y, x + 1),
        'UP': lambda y, x: (y - 1, x),
        'DOWN': lambda y, x: (y + 1, x),
    }

    def __init__(self, state):
        self.state = state

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, value):
        self._state = [[char for char in row] for row in value.split('\n') if row]

    def __iter__(self):
        return ((y, x, char) for y, row in enumerate(self.state) for x, char in enumerate(row))

    def find(self, target='b'):
        for (y, x, char) in self:
            if char == target:
                return y, x

        raise InvalidTarget()

    def set(self, y, x, value):
        target = self.state[y][x]

        if target == '#':
            raise InvalidTarget('Cannot cross #')

        self.state[y][x] = value

        if target == 'e':
            raise GameWon()

    def move(self, direction):
        direction = direction.strip()
        if direction not in self.op.keys():
            print(direction)
            raise InvalidTarget('Direction not in UP LEFT RIGHT DOWN')
        self.state = self.rotate(str(self), direction)
        pos_y, pos_x = self.find()
        next_y, next_x = self.op['UP'](pos_y, pos_x)

        self.set(pos_y, pos_x, '-')
        self.set(next_y, next_x, 'b')

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

    def out(self):
        pos_y, pos_x = self.find()
        data = [
            [self.state[pos_y - 1][pos_x - 1], self.state[pos_y - 1][pos_x + 0], self.state[pos_y - 1][pos_x + 1] ],
            [self.state[pos_y - 0][pos_x - 1], self.state[pos_y - 0][pos_x + 0], self.state[pos_y - 0][pos_x + 1] ],
            [self.state[pos_y + 1][pos_x - 1], self.state[pos_y + 1][pos_x + 0], self.state[pos_y + 1][pos_x + 1] ],
        ]
        return '\n'.join(''.join(row) for row in data)

    def __str__(self):
        return '\n'.join(''.join(row) for row in self.state)


class InvalidTarget(Exception):
    pass


class GameWon(Exception):
    pass


def run(command, stdin):
    with subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                          universal_newlines=True) as p:
        stdout, stderr = p.communicate(stdin)
    return tuple(map(str.rstrip, (stdin, stdout, stderr)))


def main():
    init = dedent("""
        #######
        #--#--#
        #--#b-#
        #--#--#
        e-----#
        #-----#
        #######
    """[1:]).rstrip()

    board = Board(init)
    moves = []

    with TemporaryDirectory() as tmpdir:
        exec_file = shutil.copy(os.path.join(BASE_PATH, TARGET), os.path.join(tmpdir, TARGET))
        os.chdir(tmpdir)

        command = EXECUTABLE, exec_file

        for move in range(200):
            try:
                stdin, stdout, stderr = run(command, '1\n'+ board.out())
                board.move(stdout)
            except GameWon:
                break
            except InvalidTarget as e:
                print(e)
                break
            finally:
                print()
                if stderr:
                    print('STDERR')
                    print(stderr)
                print('STDIN    STDOUT', stdout)
                print(stdin)
                moves.append({
                    'move': move,
                    'stdin': stdin,
                    'stdout': stdout,
                    'stderr': stderr,
                })
    with open(os.path.join(BASE_PATH, REPLAY), 'w') as f:
        json.dump(moves, f, sort_keys=True, indent=4)


if __name__ == '__main__':
    main()
