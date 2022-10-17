"""Prique implemented as a tree.

TODO: implement in C using B-tree data structure.

Binary Pivot:

    A             B
   / \           / \
  B   C   <=>   D   A
 / \               / \
D   E             E   C

  == right rotation ==>
 <==  left rotation ==

Leaf nodes are double-linked list of values and keys.
Non-leaf nodes are binary.
Rotation happens only with non-leaf nodes.
Track head and tail in Prique, double-linked list node ends.
How to handle duplicate keys? Allow left <= node <= right.
Node value is greatest in left tree.

TODO: Dynamic dispatch required. How to call node_add vs leaf_add?
- Layout structs with slots for methods
TODO: Use reference counting or malloc and free?
- Use reference counting. Much safer.
TODO: What happens when node/leaf is unlinked? Is each operation atomic?
    What about iterators and modifiers?
- No problem with reference counting.
TODO: Use PyErr_CheckSignals or cysignals in all loops?
- Test it first.
TODO: Can we make Branch nodes not ref counted? Does it make sense to do so?
- This is the approach taken by the rbtree module.
- This is the approach taken by the deque type in the collections module.
- I'm still pretty confident we want the leaves to be ref counted so we can
  iterate them safely in a multi-threaded environment.
  - I think rbtree has predecessor_node() and successor_node() API for this
    reason.
  - Consider: we're iterating (key, value) pairs so the GIL makes each operation
    atomic. We need to re-enter on calls to next().
  - Consider the "threadsafe" deque module which has no locks... except GIL!
    - I don't get how the gilectomy can work. The interpreter is rife with
      assumptions that only one thread is executing at a time.
    - I wonder how this impacts the PyPy scenario? I guess this module won't
      work with PyPY, period. How can it? We hold PyObject* references.


"""

from collections import Sequence
from cpython cimport PyObject, Py_INCREF, Py_DECREF
from itertools import izip

# TODO: Probably want SIZE closer to 64 or 128.
# Does it need to be a power of 2? Probably not.

DEF SIZE = 8


cdef class Node:
    cdef Py_ssize_t _tally
    cdef Node _head, _tail


cdef class Tree(Node):
    cdef Tree _add(self, object key, object value):
        raise NotImplementedError
    cdef Tree _discard(self, object key, object value):
        raise NotImplementedError
    cdef bint _contains(self, object key, object value):
        raise NotImplementedError
    cdef _getitem(self, Py_ssize_t index):
        raise NotImplementedError


NONE = Tree()


cdef class Prique(Node):
    'Priority Queue'

    cdef Tree _root


    def __init__(self, items=()):
        self._tally = 0
        self._head = self
        self._tail = self
        self._root = None
        self.__update(items)


    def __repr__(self):
        return '%s(%r)' % (type(self).__name__, list(self))


    # MutableSet Methods


    def add(self, key, value):
        cdef Tree root = self._root

        if root is None:
            root = Leaf(
                tally=0,
                head=self,
                tail=self,
            )
            self._head = root
            self._tail = root

        self._root = root._add(key, value)
        self._tally += 1


    __add = add


    def discard(self, key, value):
        cdef Tree root = self._root

        if root is None:
            return

        root = root._discard(key, value)

        if root is NONE:
            return

        self._root = root
        self._tally -= 1


    def __contains__(self, item):
        key, value = item
        cdef Tree root = self._root
        return False if root is None else root._contains(key, value)


    def __iter__(self):
        return PriqueIterator(self._head, 0, self._tally)


    def __len__(self):
        return self._tally


    def clear(self):
        self._tally = 0
        self._head = self
        self._tail = self
        self._root = None


    def remove(self, key, value):
        cdef Tree root = self._root

        if root is None:
            raise KeyError

        root = root._discard(key, value)

        if root is NONE:
            raise KeyError

        self._root = root
        self._tally -= 1


    def update(self, items):
        # TODO: Provide fast-path when len(items) >> len(self).
        add = self.__add

        for key, value in items:
            add(key, value)


    __update = update


    # Comparison Methods


    def __eq__(self, other):
        cdef Node node
        cdef Leaf leaf
        cdef PyObject ** keys
        cdef PyObject ** values

        if not isinstance(other, Prique):
            return NotImplemented

        if self is other:
            return True

        if self._tally != len(other):
            return False

        return all(alpha == beta for alpha, beta in izip(self, other))


    def __ne__(self, other):
        cdef Node node
        cdef Leaf leaf
        cdef PyObject ** keys
        cdef PyObject ** values

        if not isinstance(other, Prique):
            return NotImplemented

        if self is other:
            return False

        if self._tally != len(other):
            return True

        return any(alpha != beta for alpha, beta in izip(self, other))


    # Sequence Methods


    def __getitem__(self, index):
        cdef Py_ssize_t tally = self._tally
        cdef Py_ssize_t pos = index

        if pos < 0:
            pos += tally

        if pos < 0:
            raise IndexError

        if pos >= tally:
            raise IndexError

        return self._root._getitem(pos)


    def __reversed__(self):
        return PriqueReverseIterator(self._tail, 1, self._tally)


    def index(self, key, value):
        root = self._root

        if root is None:
            raise ValueError

        return root.index(key, value)


    def count(self, key, value):
        root = self._root
        return 0 if root is None else root.count(key, value)


    # MutableMapping Methods


    def get(self, key):
        root = self._root

        if root is None:
            raise KeyError

        value = root.get(key)

        if <void *>value is NULL:
            raise KeyError

        return value


    def pop(self, key):
        root = self._root

        if root is None:
            raise KeyError

        root, value = root.pop(key)

        if <void *>root is NULL:
            raise KeyError

        self._root = root
        return key, value


    def popitem(self, index=-1):
        tally = self._tally

        if index < 0:
            index += tally

        if index < 0:
            raise IndexError

        if index >= tally:
            raise IndexError

        root, key, value = self._root.pop(index)
        self._root = root
        return key, value


    # Extension Methods


    def __copy__(self):
        type_self = type(self)
        return type_self(self)


    copy = __copy__


    def __reduce__(self):
        return type(self), (list(self),)


    def bisect_left(self, key):
        root = self._root
        return 0 if root is None else root.bisect_left(key)


    def bisect_right(self, key):
        root = self._root
        return 0 if root is None else root.bisect_right(key)


    def change(self, value, old_key, new_key):
        root = self._root

        if root is None:
            raise ValueError

        status = root.change(value, old_key, new_key)

        if status == 'not found':
            raise ValueError
        elif status == 'changed':
            return
        else:
            assert status == 'discarded'
            self._add(self, new_key, value)


    def irange(self, min_key=None, max_key=None, exc_min=True, exc_max=True,
               reverse=False):
        pass


    def islice(self, start=None, stop=None, reverse=False):
        cdef Py_ssize_t tally = self._tally

        if start is None:
            cdef Py_ssize_t start_ = 0

        if start_ < 0:
            start_ += tally

        if start_ < 0:
            start_ = 0

        if start_ >= tally:
            start_ = tally

        if stop is None:
            cdef Py_ssize_t stop_ = tally

        if stop_ < 0:
            stop_ += tally

        if stop_ < 0:
            stop_ = 0

        if stop_ >= tally:
            stop_ = tally

        # TODO: How to lookup leaf and offset index?


Sequence.register(Prique)


cdef class PriqueIterator:
    cdef Leaf _leaf
    cdef Py_ssize_t _index
    cdef Py_ssize_t _count

    def __cinit__(self, leaf, index, count):
        self._leaf = leaf
        self._index = index
        self._count = count

    def __iter__(self):
        return self

    def __next__(self):
        cdef Py_ssize_t count = self._count

        if count == 0:
            raise StopIteration

        cdef Leaf leaf = self._leaf
        cdef Py_ssize_t index = self._index
        cdef Py_ssize_t tally = leaf._tally

        if index >= tally:
            node = leaf._tail

            if type(node) is Prique:
                self._leaf = None
                self._count = 0
                raise StopIteration

            self._leaf = <Leaf>node
            leaf = <Leaf>node
            self._index = 0
            index = 0

        key = <object>leaf.keys[index]
        value = <object>leaf.values[index]
        self._index = index + 1
        self._count = count - 1
        return key, value


cdef class Branch(Tree):
    'Prique Branch'

    cdef object key

    def __init__(self, tally, head, tail, key):
        self._tally = tally
        self._head = head
        self._tail = tail
        self.key = key


    def contains(self, key, value):
        if key <= self.key:
            return self._head.contains(key, value)
        else:
            return self._tail.contains(key, value)


    def add(self, value, key):
        if key <= self.key:
            left = self.left.add(value, key)
            self.left = left
        else:
            right = self.right.add(value, key)
            self.right = right

        self._tally += 1

        return self.balance()

    def balance(self):
        return self


cdef Py_ssize_t bisect_left(PyObject ** items, object value, Py_ssize_t size):
    """Return the `index` to insert `value` in `items` with given `size`.

    Assumes `items` is sorted.

    The return value, `index`, is such that all elements in `items[:index]` are
    less than `value` and all elements in `items[index:]` are greater than or
    equal to `value`. So if `value` already appears in `items`, `index` points
    just before the leftmost item already there.

    The `size` corresponds to the size of the `items` array.

    """
    cdef Py_ssize_t low = 0
    cdef Py_ssize_t high = size
    cdef Py_ssize_t middle
    cdef object item

    while low < high:
        middle = (low + high) / 2
        item = <object>items[middle]

        if item < value:
            low = middle + 1
        else:
            high = middle

    return low



cdef void insert(PyObject ** items, Py_ssize_t index, object item, Py_ssize_t size):
    """Insert `item` at `index` in `items` with given `size`.

    """
    while size > index:
        items[size] = items[size - 1]
        size -= 1

    Py_INCREF(item)
    items[index] = <PyObject * >item


cdef Py_ssize_t bisect_right(PyObject ** items, object value, Py_ssize_t size):
    """Return the `index` to insert `value` in `items`, bound by `size`.

    Assumes `items` is sorted.

    The return value, `index`, is such that all elements in `items[:index]` are
    less than or equal to `value` and all elements in `items[index:]` are
    greater than `value`. So if `value` already appears in `items`, `index`
    points just beyond the rightmost item already there.

    """
    cdef Py_ssize_t low = 0
    cdef Py_ssize_t high = size
    cdef Py_ssize_t middle
    cdef object item

    while low < high:
        middle = (low + high) >> 1
        item = <object>items[middle]

        if value < item:
            high = middle
        else:
            low = middle + 1

    return low


cdef class Leaf(Tree):
    """Prique Leaf

    """
    cdef PyObject * keys[SIZE]
    cdef PyObject * values[SIZE]


    def __cinit__(self, Py_ssize_t tally, Node head, Node tail):
        """Initialize leaf node.

        Increment reference counts on keys and values.

        To access a key, use a cast:

        cdef object key = <object>self.keys[0]

        """
        self._tally = tally
        self._head = head
        self._tail = tail


    def __dealloc__(self):
        keys = self.keys
        values = self.values

        for index in range(self._tally):
            Py_DECREF(<object>keys[index])
            keys[index] = NULL
            Py_DECREF(<object>values[index])
            values[index] = NULL


    def contains(self, Node root, object key, object value):
        cdef Node node = self
        cdef Py_ssize_t tally = self._tally
        cdef PyObject ** keys = self.keys
        cdef PyObject ** values = self.values
        cdef Py_ssize_t index = bisect_left(keys, key, tally)

        while index < tally and key == <object>keys[index]:
            if value == <object>values[index]:
                return True

            index += 1

            if index == tally:
                node = node._tail

                if node is root:
                    return False

                tally = node._tally
                keys = (<Leaf>node).keys
                values = (<Leaf>node).values
                index = 0

        return False


    def add(self, key, value):
        tally = self._tally
        values = self.values
        keys = self.keys

        index = bisect_right(keys, key, tally)

        if tally < SIZE:
            # Early-out case: there's room in the leaf for another (key, value)
            # pair.

            insert(keys, index, key, tally)
            insert(values, index, value, tally)
            self._tally += 1

            return self

        # Complicated case: split the leaf and return new branch.
        # Re-use this leaf as left leaf.

        left = self
        half = SIZE // 2

        right = Leaf(
            tally=half,            # Assumes HALF = SIZE / 2
            head=left,             # Previous leaf is left.
            tail=left._tail,        # Next leaf is left's next.
        )

        # TODO: Copy keys and values to `right` Leaf node.

        # Maintain doubly-linked list of leafs.

        left._tail = right

        # Update fields now that right has copies.

        self._tally = half

        for index in range(half, SIZE):
            # Do NOT use del, lists are intended to mimic arrays.
            keys[index] = NULL
            values[index] = NULL

        # Insert (value, key) pair.

        if index < half:
            insert(keys, index, key, tally)
            insert(values, index, value, tally)
            self._tally += 1
        else:
            temp = index - half
            insert(right.keys, temp, key, half)
            insert(right.values, temp, value, half)
            right._tally += 1

        # Create node to reference left and right leafs.

        branch = Branch(
            tally=tally + 1,
            head=self,
            tail=right,
            key=<object>keys[half - 1],
        )

        return branch
