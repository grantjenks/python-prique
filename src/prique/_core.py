"""Prique Core

Use Cython in pure-Python mode! No pxd necessary!

For delete, two scenarios:
1. Rebalance with neighbor
2. Shift items to neighbor and delete
Can the path of pivots necessary be proven?

"""


import cython


def insort(keys, key):
    return 0


class Prique:
    def init(self):
        self._tree = None


    def add(self, key, value):
        if self._tree is None:
            branch = Branch()
            leaf = Leaf()

            branch._parent = None
            branch._total = 1
            branch._max = key
            branch._left = leaf
            branch._right = None

            leaf._parent = branch
            leaf._total = 1
            leaf._left = None
            leaf._right = None
            leaf._keys = [key]
            leaf._values = [value]

            self._tree = branch
            return 0

        branch = self._tree

        while type(branch) is not Leaf:
            if branch._left is None:
                branch = branch._right
            elif branch._right is None:
                branch = branch._left
            elif key < branch._left._max:
                branch = branch._left
            else:
                branch = branch._right

        leaf = branch

        if leaf._total < 33:
            index = insort(leaf._keys, key)
            leaf._values.insert(index, value)
            leaf._total += 1
            if index == leaf._total:
                leaf._max = key
            branch = leaf._parent
            while branch is not None:
                branch._total += 1
                branch = branch._parent
                # TODO: Might this require rebalancing?


    def discard(self, key, value):
        if self._tree is None:
            return False
        pass  # TODO


    def len(self):
        return self._tree._total


class Branch:
    pass
    # _parent = None
    # _total = 0
    # _max = None
    # _left = None
    # _right = None


class Leaf:
    pass
    # _parent = None
    # _count = 0
    # _next = None
    # _prev = None
    # _keys = [None] * MAX_NODE_SIZE
    # _values = [None] * MAX_NODE_SIZE
