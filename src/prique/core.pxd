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

    cpdef init(self)

    @cython.locals(branch=Branch, leaf=Leaf)
    cpdef int add(self, object key, object value)

    cpdef int discard(self, object key, object value)

    cpdef int len(self)

    cpdef int check(self)
