from .main import most_common


def test_show_most_common_3():
    text = 'qwertyuiopasdfghjklzxcvbnm'
    top_three = most_common(text, 3)
    assert top_three == [('a', 1), ('b', 1), ('c', 1)]
