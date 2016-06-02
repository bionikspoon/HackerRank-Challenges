from collections import Counter, OrderedDict
from fileinput import input


class OrderedCounter(Counter, OrderedDict):
    def __init__(self, items):
        super(OrderedCounter, self).__init__(sorted(items))


def most_common(text, n):
    counts = OrderedCounter(text)
    return counts.most_common(n)


def main():
    text = input()[0]
    for letter, count in most_common(text, 3):
        print(letter, count)


if __name__ == '__main__':
    main()
