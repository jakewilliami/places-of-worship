from collections.abc import Iterable
from typing import TypeVar

T = TypeVar("T")

# https://python-patterns.guide/python/sentinel-object/
# https://www.youtube.com/watch?v=pIRNZ5Pg5UY
_STOP_ITERATION = object()


def only(x: Iterable[T]) -> T:
    """
    Helper method to return the one and only element of a collection `x`, and
    throws a `ValueError` if the collection has zero or multiple elements.

    Inspired by Julia's `only` function:
      <github.com/JuliaLang/julia/blob/7fa26f01/base/iterators.jl#L1500-L1549>

    See also:
      <github.com/more-itertools/more-itertools/blob/5ad93fe6/more_itertools/more.py#L3510-L3544>
      <github.com/pypa/setuptools/blob/1fe0c5d2/setuptools/_vendor/more_itertools/more.py#L3300-L3338>
    """
    if not isinstance(x, Iterable):
        raise TypeError("Cannot get only value from non-iterable object")

    itr = iter(x)
    i = next(itr, _STOP_ITERATION)

    if i is _STOP_ITERATION:
        raise ValueError("Collection is empty; must contain exactly 1 element")

    if next(itr, _STOP_ITERATION) is not _STOP_ITERATION:
        raise ValueError(
            "Collection has multiple elements; must contain exactly 1 element"
        )

    return i
