from __future__ import annotations

import ast
import sys
from typing import Callable
from typing import Hashable
from typing import Iterator
from typing import List
from typing import TypeVar
from typing import Union

# Recursive value type used in AST comparisons: can be an AST node, a list of
# values, or a primitive leaf value. We use a forward reference for the list
# element type so the alias can be recursive.
Value = Union[ast.AST, List["Value"], str, int, float, bytes, bool, None]

if sys.version_info >= (3, 9):
    from ast import unparse
else:
    from astunparse import unparse  # type: ignore


def ast_dump(node: ast.AST) -> str:
    if sys.version_info >= (3, 9):
        return ast.dump(node, indent=2)
    return ast.dump(node)


def arguments(
    node: ast.FunctionDef | ast.AsyncFunctionDef | ast.Lambda,
) -> list[ast.arg]:
    args = node.args
    l: list[ast.arg | None] = [
        *args.args,
        args.vararg,
        *args.kwonlyargs,
        args.kwarg,
    ]

    l += args.posonlyargs

    return [arg for arg in l if arg is not None]  # type: ignore[return-value]


def walk_until(
    node: ast.AST | list, stop: type | tuple[type, ...]
) -> Iterator[ast.AST | list]:
    if isinstance(node, stop):
        return
    yield node
    if isinstance(node, list):
        for e in node:
            yield from walk_until(e, stop)
        return
    for child in ast.iter_child_nodes(node):
        yield from walk_until(child, stop)


def walk_childs_first(node: ast.AST) -> Iterator[ast.AST]:
    for e in ast.iter_child_nodes(node):
        yield from walk_childs_first(e)
        yield e


def walk_function_nodes(node: ast.AST | list) -> Iterator[ast.AST | list]:
    if isinstance(node, (ast.AsyncFunctionDef, ast.FunctionDef, ast.Lambda)):
        for argument in arguments(node):
            if argument.annotation:
                yield from walk_function_nodes(argument.annotation)
        for default in [*node.args.kw_defaults, *node.args.defaults]:
            if default is not None:
                yield from walk_function_nodes(default)

        if isinstance(node, (ast.AsyncFunctionDef, ast.FunctionDef)):
            for decorator in node.decorator_list:
                yield from walk_function_nodes(decorator)

            if node.returns is not None:
                yield from walk_function_nodes(node.returns)

        return
    yield node
    if isinstance(node, list):
        for e in node:
            yield from walk_function_nodes(e)
        return
    for child in ast.iter_child_nodes(node):
        yield from walk_function_nodes(child)


def equal_ast(
    lhs: Value,
    rhs: Value,
    print: Callable[..., None] = lambda *args: None,
    t: str = "root",
) -> bool:
    if type(lhs) != type(rhs):
        print(t, lhs, "!=", rhs)
        return False

    elif isinstance(lhs, list):
        assert isinstance(rhs, list)
        if len(lhs) != len(rhs):
            print(t, lhs, "!=", rhs)
            return False

        return all(
            equal_ast(l, r, print, t + f"[{i}]")
            for i, (l, r) in enumerate(zip(lhs, rhs))
        )

    elif isinstance(lhs, ast.AST):
        return all(
            equal_ast(getattr(lhs, field), getattr(rhs, field), print, t + f".{field}")
            for field in lhs._fields
        )
    else:
        if lhs != rhs:
            print(t, lhs, "!=", rhs)
        return lhs == rhs


T = TypeVar("T")


def only_firstone(l: list[T], condition: Callable[[T], bool]) -> None:
    found = False
    for i, e in reversed(list(enumerate(l))):
        if condition(e):
            if found:
                del l[i]
            found = True


def unique_by(l: list[T], key: Callable[[T], Hashable]) -> list[T]:
    return list({key(e): e for e in l}.values())
