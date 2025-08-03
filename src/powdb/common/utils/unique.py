from collections.abc import Iterable, Iterator, Mapping
from typing import TypeVar

T, U = TypeVar("T"), TypeVar("U")


def in_mut(x: T, s: list[T]) -> bool:
    """
    If `x` is in `s`, return true.  If not, push `x` into `s` and return false.

    This is equivalent to
        x in s or s.add(x) or False

    Or in Julia:
        x in s ? true : (push!(s, x); false)

    Inspired by Julia's `in!` function:
      <github.com/JuliaLang/julia/blob/7fa26f01/base/set.jl#L94-L135>
    """
    if x in s:
        return True

    s.append(x)
    return False


def _items(x: Iterable[T]) -> Iterator[U]:
    if isinstance(x, Mapping):
        yield from x.items()
    else:
        yield from x


def unique(x: Iterable[T]) -> list[T]:
    """
    Return an array containing only the unique elements of the collection, as
    determed by their hash, in the order that the first of each set of
    equivalent elements originally apprars.

    The container type of the input is preserved with `empty`.

    `x` must be some container that implements the `__len__()` and `__getitem__`
    methods.

    Inspired by Julia's `unique` function:
      <github.com/JuliaLang/julia/blob/7fa26f01/base/set.jl#L200-L478>
      <github.com/JuliaLang/julia/blob/7fa26f01/base/multidimensional.jl#L1714-L1834>
    """
    # TODO
    if not isinstance(x, Iterable):
        raise TypeError("Cannot compute unique elements of non-iterable type")

    # NOTE: `seen` must be a list as items of x may be unhashable
    seen, out = list(), list()

    for e in _items(x):
        in_mut(e, seen) or out.append(e)

    return out
