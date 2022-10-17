"""Prique

Simple reference implementation focused on API design.
"""

from bisect import bisect_left, bisect_right
from collections import Sequence


class Prique(Sequence):
    """Priority Queue

    """

    def __init__(self, items=()):
        self._keys = []
        self._values = []
        pairs = sorted(items, key=lambda item: item[0])
        self._keys[:] = [pair[0] for pair in pairs]
        self._values[:] = [pair[1] for pair in pairs]


    def __repr__(self):
        return '%s(%r)' % (type(self).__name__, list(self))


    # MutableSet Methods


    def add(self, key, value):
        index = bisect_right(self._keys, key)
        self._keys.insert(index, key)
        self._values.insert(index, value)


    def discard(self, key, value):
        limit = len(self._keys)
        index = bisect_left(self._keys, key)

        while index < limit and key == self._keys[index]:
            if value == self._values[index]:
                del self._values[index]
                del self._keys[index]
                return True

            index += 1

        return False


    def contains(self, key, value):
        limit = len(self._keys)
        index = bisect_left(self._keys, key)

        while index < limit and key == self._keys[index]:
            if value == self._values[index]:
                return True

            index += 1

        return False


    def iter(self):
        return self.islice()


    def len(self):
        return len(self._keys)


    def clear(self):
        del self._values[:]
        del self._keys[:]


    # Comparison Methods


    def eq(self, other):
        if not isinstance(other, Sequence):
            return NotImplemented

        return (
            len(self) == len(other)
            and all(item == iota for item, iota in zip(self, other))
        )


    def ne(self, other):
        if not isinstance(other, Sequence):
            return NotImplemented

        return (
            len(self) != len(other)
            or any(item != iota for item, iota in zip(self, other))
        )


    # Sequence Methods


    def getitem(self, index):
        assert not isinstance(index, slice)
        return self._keys[index], self._values[index]


    def _setitem(self, index, key, value):
        # Dangerous API!
        self._keys[index] = key
        self._values[index] = value


    def delitem(self, index):
        del self._keys[index]
        del self._values[index]


    def _insert(self, index, key, value):
        # Dangerous API!
        self._keys.insert(index, key)
        self._values.insert(index, value)


    def reversed(self):
        return self.islice(reverse=True)


    def index(self, key, value):
        limit = len(self._keys)
        key = bisect_left(self._keys, key)

        while index < limit and key == self._keys[index]:
            if value == self._values[index]:
                return index

            index += 1

        raise ValueError


    def count(self, key, value):
        total = 0
        limit = len(self._keys)
        index = bisect_left(self._keys, key)

        while index < limit and key == self._keys[index]:
            if self._values[index] == value:
                total += 1

            index += 1

        return total


    # MutableMapping Methods


    def get(self, key):
        index = bisect_left(self._keys, key)

        if key == self._keys[index]:
            return self._values[index]

        raise KeyError


    def pop(self, key):
        index = bisect_left(self._keys, key)

        if key == self._keys[index]:
            pop_key = self._keys.pop(index)
            value = self._values.pop(index)
            return pop_key, value

        raise KeyError


    def popitem(self, index=-1):
        key = self._keys.pop(index)
        value = self._values.pop(index)
        return key, value


    # Extension Methods


    def copy(self):
        type_self = type(self)
        return type_self(self)


    def __reduce__(self):
        return type(self), (list(self),)


    def bisect_left(self, key):
        return bisect_left(self._keys, key)


    def bisect_right(self, key):
        return bisect_right(self._keys, key)


    bisect = bisect_right


    def change(self, value, old_key, new_key):
        success = self.discard(value, old_key)

        if not success:
            raise ValueError

        self.add(new_key, value)


    def irange(self, min_key=None, max_key=None, exc_min=False, exc_max=False,
               reverse=False):
        "Iterate items with keys between min key and max key."
        if exc_min:
            start = self.bisect_right(min_key)
        else:
            start = self.bisect_left(min_key)

        if exc_max:
            stop = self.bisect_left(max_key)
        else:
            stop = self.bisect_right(max_key)

        return self.islice(start, stop, reverse)


    def islice(self, start=None, stop=None, reverse=False):
        "Iterate items with index between start and stop."
        keys = self._keys[start:stop]
        values = self._values[start:stop]
        pairs = list(zip(keys, values))
        iterator = reversed if reverse else iter
        return iterator(pairs)


if __name__ == '__main__':
    pairs = [(value, index) for index, value in enumerate('abcd')]
    prique = Prique(pairs * 2)

    for key, value in pairs:
        prique.add(key, value)

    assert list(prique) == sorted(pairs * 3)
    assert list(reversed(prique)) == sorted(pairs * 3, reverse=True)

    for key, value in pairs:
        item = key, value
        assert item in prique
        assert prique.count(key, value) == 3
        prique.discard(key, value)

    assert len(prique) == len(pairs) * 2
