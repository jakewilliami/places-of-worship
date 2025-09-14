from collections.abc import Iterator, Sequence
from itertools import batched


def partition[T](x: Sequence[T], n: int) -> Iterator[tuple[T]]:
    """
    Helper metthod to partition an array `x` into equal blocks of size `n`,
    with the final block containing potentially fewer than `n` elements if the
    size of `ns` is not divisible by `n`.

    Since v0.0.6, `partition` is a light wrapper around `itertools.batched`:
      <github.com/jakewilliami/places-of-worship/blob/v0.0.5/src/powdb/common/utils/partition.py>
      <stackoverflow.com/a/75981543>

    See also:
      <github.com/JuliaLang/julia/blob/7fa26f01/base/iterators.jl#L1294-L1318>
    """
    yield from batched(x, n)
