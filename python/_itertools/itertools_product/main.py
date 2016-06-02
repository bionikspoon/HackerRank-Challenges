from fileinput import input
from itertools import product


def parse_input(data):
    a, b = [map(int, line.split()) for line in data]
    return a, b


def main():
    a, b = parse_input(input())
    print(' '.join(map(str, product(a, b))))


if __name__ == '__main__':
    main()
