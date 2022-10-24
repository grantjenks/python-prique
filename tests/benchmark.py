import sortedcontainers
import random
import timeit

from bintrees import AVLTree, RBTree  # Works on Python 3.9
from collections import deque
from itertools import starmap
from prique import core

print(core.__file__)
rand = random.Random(0)
# values = [rand.randrange(1000) for _ in range(1_000_000)]
values = list(range(1_000_000))
rand.shuffle(values)
pairs = list(zip(values, values))

times = timeit.repeat(
    'deque(map(s.add, values), maxlen=0)',
    setup='s = sortedcontainers.SortedList()',
    repeat=5,
    number=1,
    globals=globals(),
)

print('SortedList:', times)

times = timeit.repeat(
    'deque(starmap(p.add_left, pairs), maxlen=0)',
    setup='p = core.Prique(); p.init()',
    repeat=5,
    number=1,
    globals=globals(),
)

print('Prique:', times)

times = timeit.repeat(
    'deque(starmap(r.insert, pairs), maxlen=0)',
    setup='r = RBTree()',
    repeat=5,
    number=1,
    globals=globals(),
)

print('RBTree:', times)

# times = timeit.repeat(
#     'r.update(pairs)',
#     setup='r = AVLTree()',
#     repeat=5,
#     number=1,
#     globals=globals(),
# )

# print('AVLTree:', times)
