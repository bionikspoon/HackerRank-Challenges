from fileinput import input
from itertools import permutations


def parse_input(data):
    text, n = data.split()
    return text, int(n)


def main():
    text, n = parse_input(input()[0])
    for permutation in sorted(permutations(text, n)):
        print(''.join(permutation))


if __name__ == '__main__':
    main()
