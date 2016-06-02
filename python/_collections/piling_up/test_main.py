from collections import deque, namedtuple

import pytest

from .main import pop_next, can_stack


def test_it_pops_right_when_right_is_larger():
    cubes = deque((1, 3, 2))
    assert pop_next(cubes) == 2


def test_it_pops_left_when_left_is_larger():
    cubes = deque((3, 4, 2))
    assert pop_next(cubes) == 3


def test_it_pops_last_when_len_is_one():
    cubes = deque((4,))
    assert pop_next(cubes) == 4


def test_it_returns_none_when_len_is_zero():
    cubes = deque()
    assert pop_next(cubes) is None


Case = namedtuple('Case', 'cubes expected')
tests = [
    Case(deque([4, 3, 2, 1, 3, 4]), True),
    Case(deque([1, 3, 2]), False),
]


@pytest.mark.parametrize('case', tests)
def test_can_stack(case):

    assert can_stack(case.cubes) == case.expected
