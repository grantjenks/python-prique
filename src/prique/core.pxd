import cython


cdef int MAX_LEAF_SIZE
cdef int MAX_LEAF_SIZE_SUB1
cdef int MAX_LEAF_SIZE_DIV2
cdef int MAX_LEAF_SIZE_MUL2
cdef int MIN_LEAF_SIZE
cdef int AVG_LEAF_SIZE


cdef int bisect_left(list values, object value)


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

    cpdef int add_left(self, object key, object value)

    cpdef int discard(self, object key, object value)

    cpdef int len(self)

    cdef _pivot_left(self, Branch branch)

    cdef _pivot_right(self, Branch branch)
