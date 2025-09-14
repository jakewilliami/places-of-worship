from collections.abc import Container, Iterable, Iterator, Mapping
from functools import reduce
from itertools import chain
from types import GenericAlias
from typing import Any, Never, NoReturn, get_args, get_origin

from .only import only


def _only_or_identity[T](x: Iterable[T]) -> Iterable[T] | T:
    try:
        return only(x)
    except ValueError:
        return x


def _is_immutable_container[T](x: Container[T]) -> bool:
    # TODO: expand this to be inclusive of at least stdlib.
    #
    # For now, this fits my needs, but in future might want to check against
    # something like `hasattr(x, '__setitem__')`.
    return isinstance(x, (tuple, frozenset))


def _type_union_t(types: Iterable[type]) -> type:
    return reduce(lambda a, b: a | b, types)


def _type_union[T](x: Iterable[T]) -> type:
    # Given a collection of types, find their union type

    # As we need to iterate over x more than once, we must make a greedy copy
    # of it so that it is not consumed
    if isinstance(x, Iterator):
        x = list(x)

    # If the iterable is invalid, we can't infer the type, so we return Any
    #
    # However, we must give special handling to the possibility that we have
    # an empty tuple whose element type cannot be inferred.  In this case, we
    # return the bottom type; see case 2 in `_typeof_tuples`.  In fact, this
    # is true for any empty immutable container.  Another example of this in
    # base Python is the frozenset
    if not x:
        if _is_immutable_container(x):
            return Never

        return Any

    # Special dispatch required for union-ing of tuples
    #
    # We use a for-append pattern rather than list comprehension twice:
    #     tuple_types = [e for e in x if isinstance(e, tuple)]
    #     rest = set(_type(e) for e in x if not isinstance(e, tuple))
    #
    # This is preferrable so that we don't have to iterate more than once, and
    # so that order is easier to ensure with uniqueness.
    rest, tuple_types = [], []
    for e in x:
        if isinstance(e, tuple):
            tuple_types.append(e)
        else:
            t = _type(e)
            if t not in rest:
                rest.append(t)

    if tuple_types:
        rest.append(_typeof_tuples(tuple_types))

    # Final reduced union type
    return _type_union_t(rest)


def _eltype_mapping(x: Mapping) -> type:
    kt = _eltype(x.keys())
    vt = _eltype(x.values())
    return tuple[kt, vt]


def _typeof_tuples(x: tuple | list[tuple]) -> type[tuple]:
    # Case 1: optimised dispatch when passed a single tuple
    #
    # This works for the case of an empty tuple as the `for e in x` generator
    # wrapped in `tuple()` will be empty.
    if isinstance(x, tuple):
        return tuple[tuple(_type(e) for e in x)]

    # Now we can handle more complex cases of tuple typing
    ns = {len(t) for t in x}
    tt = [[e for e in t] for t in x]

    # Case 2: special handling for empty tuples
    #
    # As tuples are immutable, an empty tuple cannot change type.  However, we
    # can't know its element type at compile time, so it must be a "bottom" type
    # That is, a type ⊥, that is the subtype of all other types.
    #
    # In Julia, the eltype(()) == Base.Bottom == Union{}.  The empty union of
    # types represents a type that has no values.
    #
    # Although there are make-shift bottom types in Python (Never and NoReturn),
    # PEP 484 specifies a special type for the empty tuple: tuple[()].
    #
    #   <en.wikipedia.org/wiki/Bottom_type>
    #   <https://docs.python.org/3/library/typing.html#typing.Never>
    #   <https://docs.python.org/3/library/typing.html#typing.NoReturn>
    #   <github.com/python/mypy/issues/4211#issuecomment-342377880>
    #   <peps.python.org/pep-0484>
    has_empty = 0 in ns
    if len(ns) == 1 and has_empty:
        return tuple[()]

    if has_empty:
        # Remove the empty tuple and recompute lengths
        tt[:] = [t for t in tt if len(t) > 0]
        ns = {len(t) for t in tt}

    if len(ns) == 1:
        # Case 3: all tuples are a fixed length
        #
        # In this case, we have to organise these by column (i.e., transpose).
        # E.g., into tuples of the first element, and then the second, and so on
        #
        # We can zip these stictly because we know that they all have the same
        # number of elements.
        tt_trans = zip(*tt, strict=True)
        t = tuple[tuple(_type_union(col) for col in tt_trans)]
    else:
        # Case 4: tuple lengths differ, so we must return variable-length tuple
        t = tuple[_type_union(chain.from_iterable(tt)), ...]

    # Continued special handling for empty tuples: applying the union
    if has_empty:
        t |= tuple[()]

    return t


def _typeof_dict(x: dict) -> type[dict]:
    kt = _eltype(x.keys())
    vt = _eltype(x.values())
    return dict[kt, vt]


def _collection_type(ct: type, et: type) -> type:
    # Case 1: generic container type as we cannot infer element type
    if et == Any:
        return ct[Any]

    # Case 2: container type can be specified
    return ct[et]


def _type[T](x: T) -> type:
    # TODO: in future, expose an interface to this function so that I can
    #   make a `typeof` method.
    if not isinstance(x, Container):
        return type(x)

    if isinstance(x, str):
        return str

    if isinstance(x, Mapping):
        return _typeof_dict(x)

    if isinstance(x, tuple):
        return _typeof_tuples(x)

    # As `_type` is only used internally, it is safe to assume that once we get
    # here, we must have a collection type that is concrete and constructable
    # as a parameterised generic.  However, calling something like
    # `_type(range(10))` will not work, so if I expose a `typeof` method in
    # future, extended types will need to be accounted for.
    t = _eltype(x)
    return _collection_type(type(x), t)


def _eltype[T](x: Container[T]) -> type:
    if isinstance(x, Mapping):
        return _eltype_mapping(x)

    return _type_union(x)


# TODO: support this in future
def _eltype_t(t: type) -> type:
    origin = get_origin(t) or t
    args = get_args(t)

    # Case 1: there is no element type
    if not issubclass(origin, Container):
        return Any

    # Case 2: container type has no parameterised generic
    if not args:
        return Any

    # Case 3: mappings
    if issubclass(origin, Mapping):
        return args

    # Case 4: special handling for tuples, which may have variable arguments
    if origin is tuple:
        # Case 4.a: variable argument tuple
        if len(args) == 2 and args[1] == Ellipsis:
            return args[0]

        # Case 4.b: all elements have
        assert Ellipsis not in args
        return _only_or_identity(args)

    # Any remaining container type shouldn't have variable args
    return only(args) or Any


def eltype[T](x: T) -> type:
    """
    Return the element type of the given collection,

    If there are no elements,

    Inspired by Julia's `eltype` function:
      <github.com/JuliaLang/julia/blob/7fa26f01/base/abstractarray.jl#L219-L242>

    Only, in Python's case, this is considerably more difficult.
    """
    # TODO: in future, we may want to support eltype on types, for example
    #   list[int] would return int, int would return int, etc.

    # Explicitly error on Never or NoReturn, as these are bottom types in Python
    # which necessarily contain no elements.
    #
    # This should never actually happen.
    t = type(x)
    if t is Never or t is NoReturn:
        raise TypeError("The bottom type necessarily contains·no·elements")

    # TODO: special dispatch for types
    if isinstance(x, (type, GenericAlias)) or get_origin(t) is not None:
        return _eltype_t(x)

    # If we are given an iterator, we cannot conveniently review its contents
    # without consuming it, so we load it into memory.  Despite the potential
    # memory cost of this, it is required to check all elements so that we can
    # infer all types in the container.
    if isinstance(x, Iterator):
        x = list(x)

    # Dispatch into recursive `_eltype` method for containers.
    if isinstance(x, Container):
        return _eltype(x)

    # Any non-iterable type has element type `Any`.  This is the "top type",
    # which includes all other types as subtypes.
    #
    # Returning the bottom type (see case 2 in `_typeof_tuples`) as a default
    # might seem appealing, but that would mean "this type has no elements,"
    # which isn't necessarily true for non-iterables.  The concept of having
    # elements for non-iterables is undefined, not empty.
    #
    #   <en.wikipedia.org/wiki/Any_type>
    #   <docs.python.org/3/library/typing.html#typing.Any>
    return Any
