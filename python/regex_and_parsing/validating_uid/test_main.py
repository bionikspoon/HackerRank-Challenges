from collections import namedtuple
import pytest

from .main import (contains_match, MATCH_ALPHANUMERIC, MATCH_LENGTH_10, is_valid,
                   MATCH_REPEAT_CHARACTERS, MATCH_UPPER, MATCH_DIGIT)

validate_2_upper = contains_match(MATCH_UPPER, count=2, op='>=')
validate_3_digits = contains_match(MATCH_DIGIT, count=3, op='>=')
validate_alpha = contains_match(MATCH_ALPHANUMERIC)
validate_distinct = contains_match(MATCH_REPEAT_CHARACTERS, count=0)
validate_length_10 = contains_match(MATCH_LENGTH_10)

Case = namedtuple('Case', 'id uid validator expect')

tests = [  # :off
    Case("is valid with 2 uppercase letters",       "B1CDEF2354",   validate_2_upper,   True),
    Case("is invalid without 2 uppercase letters",  "b1cdef2354",   validate_2_upper,   False),
    Case("is invalid without 2 uppercase letters",  "0123456789",   validate_2_upper,   False),
    Case("is valid with 3 or more digits",          "B1CDEF2354",   validate_3_digits,  True),
    Case("is valid with 3 or more digits",          "01234567AB",   validate_3_digits,  True),
    Case("is invalid only 2 digits",                "B1CDEFGHI4",   validate_3_digits,  False),
    Case("is valid only alphanumeric characters",   "B1CDEF2354",   validate_alpha,     True),
    Case("is invalid with strange characters",      "B1CD???354",   validate_alpha,     False),
    Case("is invalid with strange characters",      "AB123!CDEF",   validate_alpha,     False),
    Case("is valid with 10 characters",             "B1CDEF2354",   validate_length_10, True),
    Case("is invalid with 9 characters",            "B1CDEF235",    validate_length_10, False),
    Case("is invalid with 5 characters",            "AB123",        validate_length_10, False),
    Case("is invalid with 11 characters",           "B1CDEF2354Q",  validate_length_10, False),
    Case("is valid with unique characters",         "B1CDEF2354",   validate_distinct,  True),
    Case("is invalid with repeated characters",     "B1CD102354",   validate_distinct,  False),
    Case("is invalid with repeated characters",     "1111111111",   validate_distinct,  False),
    Case("is invalid with repeated characters",     "B1CD102344",   validate_distinct,  False),
    Case("is invalid with repeated characters",     "B1CDEF235B",   validate_distinct,  False),
]  # :on


# noinspection PyArgumentList
@pytest.mark.parametrize('case', tests, ids=lambda case: ' :: '.join([case.id, case.uid]))
def test_validator(case):
    validator, uid = case.validator, case.uid

    if case.expect:
        assert validator(uid)
    else:
        assert not validator(uid)


# noinspection PyArgumentList
@pytest.mark.parametrize('case', tests, ids=lambda case: ' :: '.join([case.id, case.uid]))
def test_is_valid(case):
    uid = case.uid

    if case.expect:
        assert is_valid(uid)
    else:
        assert not is_valid(uid)


def test_is_invalid_when_empty():
    uid = ""
    assert not is_valid(uid)
