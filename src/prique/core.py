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
        branch = Branch()
        branch._parent = None
        branch._total = 0
        branch._max = None
        branch._left = None
        branch._right = None
        self._tree = branch


    def add(self, key, value):
        if self._tree._total == 0:
            branch = self._tree
            leaf = Leaf()

            leaf._parent = branch
            leaf._total = 1
            leaf._left = None
            leaf._right = None
            leaf._keys = [key]
            leaf._values = [value]

            branch._total = 1
            return 0

        branch = self._tree

        while type(branch) is not Leaf:
            if branch._left is None:
                branch = cython.cast(Branch, branch._right)
            elif branch._right is None:
                branch = cython.cast(Branch, branch._left)
            elif key < cython.cast(Branch, branch._left)._max:
                branch = cython.cast(Branch, branch._left)
            else:
                branch = cython.cast(Branch, branch._right)

        leaf = cython.cast(Leaf, branch)

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


    def check(self):
        # Use this function to check the invariants of the prique.
        _tree = self._tree

        assert _tree is not None
        assert _tree._parent is None
        assert _tree._total >= 0

        if _tree._total == 0:
            assert _tree._max is None
            assert _tree._left is None
            assert _tree._right is None
            return 0

        return 0


class Branch:
    pass


class Leaf:
    pass
