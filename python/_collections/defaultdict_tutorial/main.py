from collections import defaultdict
from fileinput import input


def parse_input(data):
    n, m = map(int, data.pop(0).split(' '))
    a, b = data[:n], data[n:n + m]
    return a, b


def create_group(words):
    group = defaultdict(list)

    for i, word in enumerate(words, 1):
        group[word].append(i)

    return group


def main():
    a, b = parse_input([line.rstrip() for line in input()])
    group = create_group(a)

    for word in b:
        indices = group.get(word, [])
        print(-1 if not indices else ' '.join(map(str, indices)))


if __name__ == '__main__':
    main()
