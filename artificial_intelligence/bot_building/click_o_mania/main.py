#! /usr/bin/env python
# coding=utf-8
import sys
from pprint import pformat


class BaseBoard(object):
    def __init__(self, y, x, state):
        self.x = x
        self.y = y

        self._state = {}
        self.state = state

    @classmethod
    def from_input(cls, data):
        meta, grid = tuple(str(i) for i in data.strip().split('\n', 1))
        y, x, _ = tuple(int(i) for i in meta.split())

        return cls(y, x, grid)

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, value):
        for y, row in enumerate(value.split('\n')):
            for x, cell in enumerate(list(row.strip())):
                self._state[(y, x)] = cell


def debug(*args, **kwargs):
    kwargs.setdefault('pformat', False)

    debugf(*args, **kwargs)


def debugf(*args, **kwargs):
    kwargs.setdefault('file', sys.stdout)

    if kwargs.pop('pformat', True):
        print(*map(pformat, args), **kwargs)
    else:
        print(*args, **kwargs)


def next_move(y, x, _, grid):
    return '1 1'


def main():
    y, x, k = [int(i) for i in sys.stdin.readline().strip().split()]
    grid = str(sys.stdin.read().strip())

    print(next_move(y, x, k, grid))


if __name__ == '__main__':
    main()
