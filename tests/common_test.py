from collections.abc import Sequence
from typing import Any, Never

import pytest

from powdb import common


def test_only_works():
    assert common.only([1]) == 1

    # Works on different iterables
    assert common.only((1,)) == 1
    assert common.only({1: 2}) == 1
    assert common.only(i for i in (1,)) == 1
    assert common.only({1: 2}.values()) == 2
    assert common.only({1: 2}.items()) == (1, 2)

    # Works with iterable non-hashable elements
    assert common.only([[]]) == []

    # Works with None element
    assert common.only([None]) is None

    # Works with custom sentinel object
    sentinel = object()
    assert common.only([sentinel]) == sentinel

    # Raises errors when there are too many or too few elements in the
    # given collection
    with pytest.raises(ValueError, match="Collection is empty"):
        common.only([])

    with pytest.raises(ValueError, match="Collection is empty"):
        common.only(x for x in [])

    with pytest.raises(ValueError, match="Collection has multiple elements"):
        common.only([1, 2])

    with pytest.raises(ValueError, match="Collection has multiple elements"):
        common.only("abc")

    with pytest.raises(ValueError, match="Collection has multiple elements"):
        common.only([None, None])

    # Raises if the input is non-iterable
    with pytest.raises(TypeError, match="non-iterable object"):
        common.only(None)

    with pytest.raises(TypeError, match="non-iterable object"):
        common.only(123)


def test_partition():
    def test_partition(xs, expected, n):
        for a, b in zip(common.partition(xs, n), expected, strict=False):
            assert a == b

    test_partition([1, 2, 3], [(1, 2), (3,)], 2)

    # Works on different collection types
    test_partition((1, 2, 3), [(1, 2), (3,)], 2)

    # WWorks on partition size larger than iterable
    test_partition([1, 2, 3], [(1, 2, 3)], 10)

    # Works with range iterator defining custom __getitem__
    test_partition(range(3), ((0, 1), (2,)), 2)

    # Works with empty iterable
    test_partition([], [()], 1)
    assert len(list(common.partition([], 1))) == 0

    # Works for partition of size equal to iterator
    test_partition([1], [(1,)], 1)

    # Works for other immutable sequences
    test_partition("hello", [("h", "e"), ("l", "l"), ("o",)], 2)
    test_partition(
        b"hello", [(ord("h"), ord("e")), (ord("l"), ord("l")), (ord("o"),)], 2
    )

    # Works on custom class with strange behaviour
    class C(Sequence):
        def __init__(self, length=10):
            self._length = length

        def __getitem__(self, index):
            if isinstance(index, slice):
                indices = range(*index.indices(self._length))
                return [69 for _ in indices]

            if 0 <= index <= self._length:
                return 69

            raise IndexError

        def __len__(self):
            return self._length

    test_partition(C(3), [(69, 69), (69, 69)], 2)
    test_partition(C(10), [tuple(69 for _ in range(9))], 9)

    # Will not work for bad partition sizes
    with pytest.raises(ValueError, match="n must be at least one"):
        list(common.partition([1, 2, 3], 0))

    # Works for iterators
    test_partition((x for x in range(3)), [(0, 1), (2,)], 2)

    # Works for non-indexable or unordered objects, using insertion order
    test_partition({1, 2, 3}, [(1, 2), (3,)], 2)
    test_partition({1: 2, 3: 4, 5: 6}, [(1, 3), (5,)], 2)

    with pytest.raises(TypeError, match="object is not iterable"):
        list(common.partition(123, 2))

    with pytest.raises(TypeError, match="object is not iterable"):
        list(common.partition(None, 2))


def test_findfirst():
    xs = [4, 3, 2, 1]
    target, expected_idx = 3, 1

    # Works for lambda predicate
    assert common.findfirst(lambda x: x == target, xs) == expected_idx
    assert xs[common.findfirst(lambda x: x == target, xs)] == target

    # Works for function predicate
    def predicate(x: int) -> bool:
        return x == target

    assert common.findfirst(predicate, xs) == expected_idx

    # Works for range
    assert common.findfirst(lambda x: x == target, range(10)) == target

    # A predicate returning true should always have index 0
    assert common.findfirst(lambda _x: True, xs) == 0

    # No match returns None
    assert common.findfirst(lambda _x: False, xs) is None

    # findfirst on empty iterable returns None
    assert common.findfirst(lambda _x: True, []) is None

    # Returns the first match if multiple elements match
    ys = [2, 1, 2]
    target_y, expected_y_idx = 2, 0
    assert common.findfirst(lambda y: y == target_y, ys) == expected_y_idx
    assert ys[expected_y_idx] == ys[2] and expected_y_idx != 2

    # Works on first truthy value
    assert common.findfirst(lambda x: x, [0, "", [], None, "non-empty"]) == 4

    # Works for non-list collections
    xs = tuple(xs)
    assert common.findfirst(lambda x: x == target, xs) == expected_idx

    # Works for iterator
    assert common.findfirst(lambda x: x == 3, (x for x in range(10))) == 3

    # Raises error on invalid inputs
    with pytest.raises(TypeError, match="non-iterable object"):
        common.findfirst(lambda _x: True, 123)

    with pytest.raises(TypeError, match="non-iterable object"):
        common.findfirst(lambda _x: True, None)

    with pytest.raises(TypeError, match="non-sequence or unordered object"):
        common.findfirst(lambda _x: True, {1, 2, 3})

    with pytest.raises(TypeError, match="non-sequence or unordered object"):
        common.findfirst(lambda _x: True, {1: 2, 3: 4, 5: 6})

    with pytest.raises(TypeError, match="non-callable predicate"):
        common.findfirst(123, [1, 2, 3])


def test_unique():
    # Works for trivial case of list
    assert common.unique([1, 2, 3, 2, 5, 1, 2, 3, 7]) == [1, 2, 3, 5, 7]

    # Returns list of elements from non-list types
    assert common.unique({1, 2, 3, 4}) == [1, 2, 3, 4]
    assert common.unique("hello") == ["h", "e", "l", "o"]
    assert common.unique({1: 2, 3: 4}) == [(1, 2), (3, 4)]

    # Works for nested elements
    assert common.unique([[1], [2], [1]]) == [[1], [2]]

    # Works on iterators
    assert common.unique([1 for _ in range(10)]) == [1]
    assert common.unique(range(10)) == list(range(10))

    # Works for mixed types
    # NOTE: float interpreted here as int
    assert common.unique([1, "1", 1.0, 1, "1"]) == [1, "1"]

    # Works for the empty set
    assert common.unique([]) == []

    # Works for types that are equal but different objects
    xs = [object(), object()]
    assert common.unique(xs) == xs

    # Raises type errors where appropriate
    with pytest.raises(TypeError, match="non-iterable type"):
        common.unique(123)

    with pytest.raises(TypeError, match="non-iterable type"):
        common.unique(None)


def test_eltype():
    # TODO: can't use `is` because int | str not is str | int
    # TODO: fix ordr of output
    # Works for single-type list
    assert common.eltype([1, 2]) is int
    assert common.eltype((1, 2, 3)) is int
    assert common.eltype({"a", "b"}) is str
    assert common.eltype(["a", "b"]) is str
    assert common.eltype("hello") is str

    # Works for strings
    assert common.eltype("a") is str

    # Works for single-type mapping
    assert common.eltype({1: 2, 3: 4}) == tuple[int, int]
    assert common.eltype({1: "a", 2: "b"}) == tuple[int, str]

    # Works for multi-type lists
    assert common.eltype((1, 2.0, "c")) == int | float | str

    # Works for multi-type mapping
    assert common.eltype({1: "a", "b": 2}) == tuple[int | str, int | str]
    assert common.eltype({1: 2, 3: 3.14}) == tuple[int, int | float]

    # Works for single types nested
    assert common.eltype([["a"], ["b", "c"]]) == list[str]
    assert common.eltype([1, 2, [3, [4, 5]]]) == int | list[int | list[int]]

    # Non-container (types that can't be broken down) are Any or themselves
    assert common.eltype(None) is Any
    assert common.eltype(1) is Any
    assert common.eltype(1.0) is Any

    # Works for tuples of varying and equal lengths, with potentially differing
    # types
    assert common.eltype([(1, 2, 3), (4, 5), (6,)]) == tuple[int, ...]
    assert common.eltype([(1, 2, 3), (4, 5, 6)]) == tuple[int, int, int]
    assert (
        common.eltype([(1, "a", 3.2), (4, "b", 6.2)]) == tuple[int, str, float]
    )
    assert common.eltype([()]) == tuple[()]
    assert common.eltype([(1, 2, 3), ()]) == tuple[int, int, int] | tuple[()]
    assert (
        common.eltype([(1, 2, 3), (1, 2), (1,), ()])
        == tuple[int, ...] | tuple[()]
    )
    assert (
        common.eltype([(1, "a", 3.2), (4, 6.2, "b")])
        == tuple[int, str | float, float | str]
    )
    assert (
        common.eltype([(1, "a", 3.2), (6.2, "b"), ("c", "b", 2, 3.4)])
        == tuple[int | str | float, ...]
    )

    # Works with immutable empty container types
    assert common.eltype(()) is Never
    assert common.eltype(frozenset()) is Never

    # Empty elements
    assert common.eltype([]) is Any
    assert common.eltype(set()) is Any
    assert common.eltype([[]]) == list[Any]
    assert common.eltype([set()]) == set[Any]

    # Works for iterators
    assert common.eltype(range(10)) is int
    assert common.eltype(x for x in range(10)) is int

    # Works on NoneType elements
    assert common.eltype([None, None]) is type(None)

    # Element type of types can also be inferred
    assert common.eltype(list[int]) is int
    assert common.eltype(list[int | str]) == int | str
    assert common.eltype(list[str | int]) == str | int
    assert common.eltype(tuple[int | str]) == int | str
    assert common.eltype(tuple[int, ...]) is int
    assert common.eltype(tuple[list[Any], int | str, tuple[int, ...]]) == (
        list[Any],
        int | str,
        tuple[int, ...],
    )
    assert common.eltype(common.eltype([[1, 2], [3, 4]])) is int
    assert common.eltype(list) is Any  # Ambiguous elements
    assert common.eltype(int) is Any  # No elements

    # Extended tests
    assert (
        common.eltype(
            {
                1: 2,
                "3": 4,
                4.2: {1: "a", (1, 2, 3): list(), 5: 3, 2: set((1, 3.4, "a"))},
            }
        )
        == tuple[
            int | str | float,
            int
            | dict[
                int | tuple[int, int, int],
                str | int | list[Any] | set[int | float | str],
            ],
        ]
    )  # very complex and nested

    # TODO: fails on list[int, ...] because who would ever type this?
    # TODO: raises
    # TODO: what is the eltype of
    #       list(tuple[int | str, str]).
    #   it should be type?  or type[tuple[...]]?
    # TODO: copy this function for typeof
