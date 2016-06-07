# coding=utf-8
from __future__ import print_function

import json
import os.path
import shutil
import subprocess
import sys
from contextlib import contextmanager
from functools import partial
from tempfile import mkdtemp
from textwrap import dedent

EXECUTABLE = sys.executable  # python interpreter
BASE_PATH = partial(os.path.join, os.path.abspath(os.path.dirname(__file__)))
TARGET = BASE_PATH('main.py')
REPLAY = BASE_PATH('moves.json')

MAX_MOVES = 50


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
            [self.state[pos_y - 1][pos_x - 1], self.state[pos_y - 1][pos_x + 0], self.state[pos_y - 1][pos_x + 1]],
            [self.state[pos_y - 0][pos_x - 1], self.state[pos_y - 0][pos_x + 0], self.state[pos_y - 0][pos_x + 1]],
            [self.state[pos_y + 1][pos_x - 1], self.state[pos_y + 1][pos_x + 0], self.state[pos_y + 1][pos_x + 1]],
        ]
        return '\n'.join(''.join(row) for row in data)

    def __str__(self):
        return '\n'.join(''.join(row) for row in self.state)


class InvalidTarget(Exception):
    pass


class GameWon(Exception):
    pass


@contextmanager
def temp_dir(copy_targets=None):
    copy_targets = copy_targets or []

    # create temp directory
    path = mkdtemp()
    tmpdir = partial(os.path.join, path)

    # copy each target into temp directory
    for target in copy_targets:
        filename = os.path.basename(target)
        shutil.copy(target, tmpdir(filename))

    # cd temp directory
    os.chdir(tmpdir())

    # yield context handle
    yield tmpdir

    # remove temp directory
    shutil.rmtree(tmpdir())


@contextmanager
def process(command, **kwargs):
    kwargs.setdefault('stdin', subprocess.PIPE)
    kwargs.setdefault('stdout', subprocess.PIPE)
    kwargs.setdefault('stderr', subprocess.PIPE)
    kwargs.setdefault('universal_newlines', True)

    # create subprocess
    handle = subprocess.Popen(command, **kwargs)

    # yield context handle
    yield handle


def run(command, stdin):
    # create subprocess context
    with process(command) as p:
        # send input, collect output
        stdout, stderr = p.communicate(input=stdin)

    return stdin, stdout.rstrip(), stderr.rstrip()


def main():
    # create initial board
    board = Board(dedent("""
        #######
        #--#--#
        #--#b-#
        #--#--#
        e-----#
        #-----#
        #######
    """)[1:-1])

    # collect moves
    moves = []

    with temp_dir(copy_targets=[TARGET]) as tmpdir:
        command = EXECUTABLE, tmpdir(TARGET)  # ("python", "main.py")

        for move in range(MAX_MOVES):
            # run command
            stdin, stdout, stderr = run(command, '1\n' + board.out())

            try:
                # update board state
                board.move(stdout)
            except GameWon:
                break
            except InvalidTarget as e:
                print(e)
                break
            finally:
                # print details about move
                print()
                if stderr:
                    print('STDERR')
                    print(stderr)
                print('STDIN    STDOUT', stdout)
                print(stdin)

                # collect details about move
                moves.append({
                    'move': move,
                    'stdin': stdin,
                    'stdout': stdout,
                    'stderr': stderr,
                })

    # dump details about move to file
    with open(REPLAY, 'w') as f:
        json.dump(moves, f, sort_keys=True, indent=2)


if __name__ == '__main__':
    main()
