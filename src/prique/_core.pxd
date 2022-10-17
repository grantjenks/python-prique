import cython


cdef int insort(list keys, object key)


cdef class Branch:
    cdef Branch _parent
    cdef int _total
    cdef object _max
    cdef object _left
    cdef object _right


cdef class Leaf(Branch):
    cdef list _keys
    cdef list _values


cdef class Prique:
    cdef Branch _tree

    cdef init(self)

    @cython.locals(branch=Branch, leaf=Leaf)
    cdef int add(self, object key, object value)

    cdef int discard(self, object key, object value)

    cdef int len(self)
