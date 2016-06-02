from collections import OrderedDict
from fileinput import input


def parse_input(data):
    _ = int(data.pop(0))
    return data


def create_counter(words):
    counter = OrderedDict()
    for word in words:
        counter[word] = counter.get(word, 0) + 1

    return counter


def main():
    words = parse_input([line.rstrip() for line in input()])
    counter = create_counter(words)

    print(len(counter))
    print(' '.join(map(str, counter.values())))


if __name__ == '__main__':
    main()
