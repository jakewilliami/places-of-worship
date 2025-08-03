from collections.abc import Iterable, Iterator, Sequence, Sized
from typing import TypeVar

T = TypeVar("T")


def partition(x: Sequence[T], n: int) -> Iterator[Sequence[T]]:
    """
    Helper metthod to partition an array `x` into equal blocks of size `n`,
    with the final block containing potentially fewer than `n` elements if the
    size of `ns` is not divisible by `n`.

    `x` must be some container that implements the `__len__()` and
    `__getitem__` methods.

    Adapted from:
      <stackoverflow.com/a/77443952>

    See also:
      <github.com/JuliaLang/julia/blob/7fa26f01/base/iterators.jl#L1294-L1318>
    """

    if not isinstance(x, Iterable):
        raise TypeError("Cannot partition non-iterable object")

    # TODO: one day we might want to support partitioning non-sequence objects
    #
    # For example, would work if we immediately make the input 1D
    #   <github.com/JuliaLang/julia/blob/7fa26f01/base/iterators.jl#L1294-L1318>
    if not isinstance(x, Sequence):
        if not isinstance(x, Sized):
            raise TypeError("Cannot partition sequence of unknown length")

        raise TypeError("Cannot partition non-indexable or unordered object")

    if n < 1:
        raise ValueError("Cannot compute non-positive partition size")

    for i in range(0, len(x), n):
        yield x[i : i + n]
