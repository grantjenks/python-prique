import itertools
import string

from prique.core import Prique


def test_cython():
    from prique import core
    assert core.__file__.endswith('.py')


def test_init():
    p = Prique()
    p.init()
    assert p.check() == 0


def test_add():
    p = Prique()
    p.init()
    p.add_left(4, 'd')
    assert p.check() == 0


def test_add_inc():
    p = Prique()
    p.init()
    letters = itertools.repeat(string.ascii_lowercase)
    for index, letter in zip(range(1000), letters):
        p.add_left(index, letter)
        assert p.check() == 0
    p.dot()


def test_add_dec():
    p = Prique()
    p.init()
    letters = itertools.repeat(string.ascii_lowercase)
    for index, letter in zip(range(0, -1000, -1), letters):
        p.add_left(index, letter)
        assert p.check() == 0
    p.dot()
