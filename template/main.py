from fileinput import input


def parse_input(data):
    _ = int(data.pop(0))
    return [op.split(' ') for op in data]


def main():
    data = parse_input([line.rstrip() for line in input()])
    print(data)


if __name__ == '__main__':
    main()
