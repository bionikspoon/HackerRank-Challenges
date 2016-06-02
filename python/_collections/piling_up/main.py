from collections import deque
from fileinput import input


def parse_input(data):
    t = int(data.pop(0))
    return [deque(map(int, data[i * 2 + 1].split())) for i in range(t)]


def can_stack(cubes):
    stack = []

    while True:
        next_cube = pop_next(cubes)
        if not next_cube:
            break
        stack.append(next_cube)

    return stack == sorted(stack, reverse=True)


def pop_next(cubes):
    if not cubes:
        return None

    if len(cubes) == 1:
        return cubes.pop()

    left, right = cubes[0], cubes[-1]

    if left >= right:
        return cubes.popleft()
    return cubes.pop()


def main():
    cases = parse_input([line.rstrip() for line in input()])
    for case in cases:
        print('Yes' if can_stack(case) else 'No')


if __name__ == '__main__':
    main()
