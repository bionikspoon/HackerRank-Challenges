from __future__ import division
from collections import namedtuple
from fileinput import input


def parse_input(data):
    _ = int(data.pop(0))
    keys = data.pop(0).split()
    Student = namedtuple('Student', keys)
    return [Student(*map(int_or_str, student.split())) for student in data]


def int_or_str(value):
    return int(value) if value.isdigit() else str(value)


def main():
    students = parse_input([line.rstrip() for line in input()])
    average = sum(student.MARKS for student in students) / len(students)

    print('%.2f' % average)


if __name__ == '__main__':
    main()
