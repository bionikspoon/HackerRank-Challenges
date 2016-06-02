from fileinput import input
from itertools import combinations_with_replacement


def parse_input(data):
    text, n = data.split()
    return text, int(n)


def create_combinations(text, n):
    return (''.join(item) for item in combinations_with_replacement(sorted(text), n))


def main():
    text, n = parse_input(input()[0])
    for combination in create_combinations(text, n):
        print(combination)


if __name__ == '__main__':
    main()
