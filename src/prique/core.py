"""Prique Core

For delete, two scenarios:
1. Rebalance with neighbor
2. Shift items to neighbor and delete
Can the path of pivots necessary be proven?

Swap position of (key, value) in APIs?

"""


if True:
    class Cython:
        def cast(self, kind, value):
            return value
    cython = Cython()
else:
    import cython


MAX_LEAF_SIZE = 8
MAX_LEAF_SIZE_SUB1 = MAX_LEAF_SIZE - 1
MAX_LEAF_SIZE_DIV2 = MAX_LEAF_SIZE >> 1
MAX_LEAF_SIZE_MUL2 = MAX_LEAF_SIZE << 1
MIN_LEAF_SIZE = MAX_LEAF_SIZE >> 2
AVG_LEAF_SIZE = MIN_LEAF_SIZE + (MAX_LEAF_SIZE - MIN_LEAF_SIZE) >> 1


def bisect_left(values, value):
    lo = 0
    hi = len(values)
    while lo < hi:
        mid = (lo + hi) // 2
        if values[mid] < value:
            lo = mid + 1
        else:
            hi = mid
    return lo


class Prique:
    def init(self):
        leaf = Leaf()
        leaf._parent = None
        leaf._total = 0
        leaf._max = None
        leaf._left = None
        leaf._right = None
        leaf._keys = []
        leaf._values = []
        self._tree = leaf

    def add_left(self, key, value):
        # TODO return index of key, value
        # Traverse to leaf for insert.

        branch = self._tree

        while type(branch) is not Leaf:
            if branch._left is None:
                branch = cython.cast(Branch, branch._right)
            elif branch._right is None:
                branch = cython.cast(Branch, branch._left)
            elif key <= cython.cast(Branch, branch._left)._max:
                branch = cython.cast(Branch, branch._left)
            else:
                branch = cython.cast(Branch, branch._right)

        leaf = cython.cast(Leaf, branch)

        # Insert key and value in leaf.

        if leaf._total < MAX_LEAF_SIZE_SUB1:
            leaf_keys = leaf._keys
            index = bisect_left(leaf_keys, key)
            leaf_keys.insert(index, key)
            leaf._values.insert(index, value)
            leaf_total = leaf._total
            new_max = (index == leaf_total)
            leaf._total = leaf_total + 1
            branch = leaf._parent

            if new_max:
                leaf._max = key
                if branch is not None and branch._right is leaf:
                    branch._max = key
        else:
            leaf_parent = leaf._parent
            old_leaf_left = leaf._left
            old_leaf_right = leaf._right
            keys = leaf._keys
            values = leaf._values
            index = bisect_left(keys, key)
            keys.insert(index, key)
            values.insert(index, value)
            new_max = (index == MAX_LEAF_SIZE_SUB1)
            keys_left = keys[:MAX_LEAF_SIZE_DIV2]
            keys_right = keys[MAX_LEAF_SIZE_DIV2:]
            values_left = values[:MAX_LEAF_SIZE_DIV2]
            values_right = values[MAX_LEAF_SIZE_DIV2:]
            branch = Branch()

            leaf_left = leaf
            leaf_left._parent = branch
            leaf_left._total = MAX_LEAF_SIZE_DIV2
            leaf_left._max = keys_left[-1]
            leaf_left._keys = keys_left
            leaf_left._values = values_left

            leaf_right = Leaf()
            leaf_right._parent = branch
            leaf_right._total = MAX_LEAF_SIZE_DIV2
            leaf_right._max = keys_right[-1]
            leaf_right._keys = keys_right
            leaf_right._values = values_right

            leaf_left._left = old_leaf_left
            leaf_left._right = leaf_right
            leaf_right._left = leaf_left
            leaf_right._right = old_leaf_right

            branch._parent = leaf_parent
            branch._total = MAX_LEAF_SIZE_SUB1
            branch._max = keys_right[-1]
            branch._left = leaf_left
            branch._right = leaf_right

            if leaf_parent is None:
                self._tree = branch
            else:
                if leaf_parent._left is leaf:
                    leaf_parent._left = branch
                else:
                    leaf_parent._right = branch

        # Traverse branch to root and update max if necessary.

        if new_max:
            max_branch = branch
            while max_branch is not None:
                max_branch_parent = max_branch._parent
                if max_branch_parent is None:
                    break
                max_branch_is_right = max_branch_parent._right is max_branch
                if max_branch_is_right:
                    max_branch_parent._max = key
                else:
                    break
                max_branch = max_branch_parent

        # Traverse branch to root, increment total, and pivot as necessary.

        while branch is not None:
            branch._total += 1
            branch_parent = branch._parent

            #   A
            #  / \
            # B   C

            branch_a_total = branch._total
            branch_b_total = branch._left._total
            branch_c_total = branch._right._total

            if branch_a_total < MAX_LEAF_SIZE_MUL2:
                pass
            elif branch_b_total > (branch_c_total << 1):
                self._pivot_right(branch)
            elif branch_c_total > (branch_b_total << 1):
                self._pivot_left(branch)

            branch = branch_parent


    def dot(self):
        print('digraph {')
        leafs = []

        def _visit(node):
            if node is None:
                return
            print(id(node), f'[label="Total: {node._total}"];')
            if node._left is not None:
                print(id(node), '->', id(node._left), ';')
            if node._right is not None:
                print(id(node), '->', id(node._right), ';')
            if type(node) is Branch:
                _visit(node._left)
                _visit(node._right)
            else:
                leafs.append(node)

        _visit(self._tree)
        print('{')
        print('    rank = same;')
        for leaf in leafs:
            print('   ', id(leaf), ';')
        print('}')
        print('}')


    def _pivot_left(self, branch):
        """Pivot left

              A
             / \
            B   C
               / \
              D   E

        Pivot:

              C
             / \
            A   E
           / \
          B   D

        """
        branch_a = branch
        branch_b = branch_a._left
        branch_c = branch_a._right
        branch_d = branch_c._left
        branch_e = branch_c._right

        branch_a_parent = branch_a._parent

        branch_b_total = branch_b._total
        branch_d_total = branch_d._total
        branch_e_total = branch_e._total

        branch_d_max = branch_d._max

        # _left, _right
        branch_a._right = branch_d
        branch_c._left = branch_a

        # _parent
        branch_a._parent = branch_c
        branch_c._parent = branch_a_parent
        branch_d._parent = branch_a

        # _total
        branch_a_total = branch_b_total + branch_d_total
        branch_a._total = branch_a_total
        branch_c._total = branch_a_total + branch_e_total

        # _max
        branch_a._max = branch_d_max

        if branch_a_parent is not None:
            if branch_a_parent._left is branch_a:
                branch_a_parent._left = branch_c
            else:
                branch_a_parent._right = branch_c

        if self._tree is branch_a:
            self._tree = branch_c


    def _pivot_right(self, branch):
        """Pivot right

              A
             / \
            B   C
           / \
          D   E

        Pivot:

              B
             / \
            D   A
               / \
              E   C

        """
        branch_a = branch
        branch_b = branch_a._left
        branch_c = branch_a._right
        branch_d = branch_b._left
        branch_e = branch_b._right

        branch_a_parent = branch_a._parent

        branch_c_total = branch_c._total
        branch_d_total = branch_d._total
        branch_e_total = branch_e._total

        branch_c_max = branch_c._max

        # _left, _right
        branch_a._left = branch_e
        branch_b._right = branch_a

        # _parent
        branch_a._parent = branch_b
        branch_b._parent = branch_a_parent
        branch_e._parent = branch_a

        # _total
        branch_a_total = branch_e_total + branch_c_total
        branch_a._total = branch_a_total
        branch_b._total = branch_d_total + branch_a_total

        # _max
        branch_b._max = branch_c_max

        if self._tree is branch_a:
            self._tree = branch_b


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
