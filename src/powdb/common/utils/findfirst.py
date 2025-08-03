from collections.abc import Callable, Iterable, Iterator, Sequence
from typing import TypeVar

T = TypeVar("T")


def findfirst(predicate: Callable[[bool], T], x: Iterable[T]) -> int | None:
    """
    Helper method to get the index of the first element in a collection `x` that
    satisfies some condition `predicate`.

    Inspired by the functionality of a Julia function of the same name:
      <github.com/JuliaLang/julia/blob/ae050a674d/base/array.jl#L2284-L2424>

    Adapted from a common pattern I've used frequently over the years:
      <stackoverflow.com/a/8534381>
    """
    if not isinstance(x, Iterable):
        raise TypeError("Cannot match from non-iterable object")

    if not isinstance(x, (Iterator, Sequence)):
        raise TypeError("Cannot match from non-sequence or unordered object")

    if not callable(predicate):
        raise TypeError("Cannot match with non-callable predicate")

    for i, e in enumerate(x):
        if predicate(e):
            return i

    return None
