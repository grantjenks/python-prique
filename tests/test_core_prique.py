from prique.core import Prique


def test_cython():
    from prique import core
    assert not core.__file__.endswith('.py')


def test_init():
    p = Prique()
    p.init()
    assert p.check() == 0
