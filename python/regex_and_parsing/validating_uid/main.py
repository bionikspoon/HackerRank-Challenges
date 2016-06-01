import re

MATCH_UPPER = re.compile(r'[A-Z]')
MATCH_DIGIT = re.compile(r'\d')
MATCH_ALPHANUMERIC = re.compile(r'^[a-zA-Z0-9]+$')
MATCH_REPEAT_CHARACTERS = re.compile(r'^.*(.).*(\1).*$')
MATCH_LENGTH_10 = re.compile(r'^.{10}$')



def is_valid(uid):
    validators = [
        # it must contain at least 2 uppercase characters
        contains_match(MATCH_UPPER, count=2, op='>='),

        # it must contain at least 3 digits
        contains_match(MATCH_DIGIT, count=3, op='>='),

        # it should only contain alphanumeric characters
        contains_match(MATCH_ALPHANUMERIC),

        # no character should repeat
        contains_match(MATCH_REPEAT_CHARACTERS, count=0),

        # there must be exactly 10 characters
        contains_match(MATCH_LENGTH_10)
    ]
    return all(validator(uid) for validator in validators)


def contains_match(regex, count=1, op='=='):
    op_def = {
        '>=': lambda a, b: a >= b,
        '==': lambda a, b: a == b,
    }

    def validator(uid):
        op_compare = op_def[op]
        return op_compare(len(regex.findall(uid)), count)

    return validator


def main():
    from fileinput import input

    # get input
    uids = [line.rstrip() for line in input()]
    n = int(uids.pop(0))

    # for each uid ... print (In)Valid
    for i in range(n):
        uid = uids[i]
        print('Valid' if is_valid(uid) else 'Invalid')


if __name__ == '__main__':
    main()
