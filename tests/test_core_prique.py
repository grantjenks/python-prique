import collections
import itertools
import random
import string

from prique.core import Prique


def test_cython():
    from prique import core
    assert core.__file__.endswith('.py')


def test_init():
    p = Prique()
    p.init()
    assert p.check() == 0
    assert p.len() == 0


def test_add():
    p = Prique()
    p.init()
    p.add_left(4, 'd')
    assert p.check() == 0
    assert p.len() == 1


def test_add_inc():
    p = Prique()
    p.init()
    letters = itertools.repeat(string.ascii_lowercase)
    for index, letter in zip(range(1000), letters):
        p.add_left(index, letter)
        assert p.check() == 0
    assert p.len() == 1000


def test_add_dec():
    p = Prique()
    p.init()
    letters = itertools.repeat(string.ascii_lowercase)
    for index, letter in zip(range(0, -1000, -1), letters):
        p.add_left(index, letter)
        assert p.check() == 0
    assert p.len() == 1000


def test_add_rand():
    p = Prique()
    p.init()
    rand = random.Random(0)
    letters = itertools.repeat(string.ascii_lowercase)
    items = list(zip(range(1000), letters))
    rand.shuffle(items)
    for index, letter in items:
        p.add_left(index, letter)
        assert p.check() == 0
    assert p.len() == 1000


def test_add_same():
    p = Prique()
    p.init()
    for i in range(1000):
        p.add_left(0, 'a')
        p.check()
    assert p.len() == 1000


def test_add_new_max():
    p = Prique()
    p.init()
    for i in range(100):
        p.add_left(i * 2, 'a')
        p.check()
    for i in range(100):
        p.add_left(81, 'b')
        p.check()
    assert p.len() == 200
