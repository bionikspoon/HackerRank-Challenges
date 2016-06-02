from fileinput import input
from itertools import combinations


def parse_input(data):
    text, n = data.split()
    return text, int(n)


def create_combinations(text, n):
    return (''.join(item) for i in range(1, n + 1) for item in combinations(sorted(text), i))


def main():
    text, n = parse_input(input()[0])
    for combination in create_combinations(text, n):
        print(combination)


if __name__ == '__main__':
    main()
