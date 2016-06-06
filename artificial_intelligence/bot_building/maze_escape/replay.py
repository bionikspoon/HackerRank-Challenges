# coding=utf-8
import json
import os.path
from time import sleep

REPLAY = 'moves.json'
BASE_PATH = os.path.abspath(os.path.dirname(__file__))


def main():
    with open(os.path.join(BASE_PATH, REPLAY)) as f:
        moves = json.load(f)

    for move in moves:
        print()
        print('{:=^40}'.format(' MOVE %s ' % move['move']))
        print()
        if move['stderr']:
            print('STDERR')
            print(move['stderr'])
            print()

        print('STDOUT')
        print(move['stdout'])
        print()

        print('STDIN')
        print(move['stdin'])
        print()

        sleep(1)


if __name__ == '__main__':
    main()
