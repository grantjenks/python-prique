import cython


cdef int MAX_LEAF_SIZE
cdef int MIN_LEAF_SIZE
cdef int AVG_LEAF_SIZE


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

    cpdef int add(self, object key, object value)

    cpdef int discard(self, object key, object value)

    cpdef int len(self)

    cpdef int check(self)

    cdef _pivot_left(self, Branch branch)

    cdef _pivot_right(self, Branch branch)
