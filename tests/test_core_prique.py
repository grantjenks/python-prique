from prique.core import Prique


def test_init():
    p = Prique()
    p.init()
    assert p.check() == 0
