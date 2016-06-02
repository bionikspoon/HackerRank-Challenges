from fileinput import input
from itertools import groupby


def main():
    text = input()[0].strip()
    groups = ((len(list(items)), int(key)) for key, items in groupby(text))
    print(' '.join(map(str, groups)))


if __name__ == '__main__':
    main()
