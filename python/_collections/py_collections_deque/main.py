from collections import deque
from fileinput import input


def parse_input(data):
    _ = int(data.pop(0))
    return [op.split(' ', 1) for op in data]


def create_stack(ops):
    stack = deque()

    def_cmd = {
        'append': lambda d, *args: d.append(*args),
        'pop': lambda d, *args: d.pop(*args),
        'popleft': lambda d, *args: d.popleft(*args),
        'appendleft': lambda d, *args: d.appendleft(*args),
    }

    for op in ops:
        cmd = def_cmd[op[0]]
        cmd_args = op[1:]
        cmd(stack, *cmd_args)

    return stack


def main():
    ops = parse_input([line.rstrip() for line in input()])
    stack = create_stack(ops)

    print(' '.join(stack))


if __name__ == '__main__':
    main()
