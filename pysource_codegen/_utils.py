from __future__ import annotations

import ast
import sys

if sys.version_info >= (3, 9):
    from ast import unparse
else:
    from astunparse import unparse  # type: ignore


def only_if(condition: bool, **kwargs) -> dict:
    return kwargs if condition else {}


def ast_dump(node):
    return ast.dump(node, **only_if(sys.version_info >= (3, 9), indent=2))


def arguments(
    node: ast.FunctionDef | ast.AsyncFunctionDef | ast.Lambda,
) -> list[ast.arg]:
    args = node.args
    l = [
        *args.args,
        args.vararg,
        *args.kwonlyargs,
        args.kwarg,
    ]

    l += args.posonlyargs

    return [arg for arg in l if arg is not None]


def walk_until(node, stop):
    if isinstance(node, stop):
        return
    yield node
    if isinstance(node, list):
        for e in node:
            yield from walk_until(e, stop)
        return
    for child in ast.iter_child_nodes(node):
        yield from walk_until(child, stop)


def walk_childs_first(node):
    for e in ast.iter_child_nodes(node):
        yield from walk_childs_first(e)
        yield e


def walk_function_nodes(node):
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


def equal_ast(lhs, rhs, print=lambda *l: None, t="root"):
    if type(lhs) != type(rhs):
        print(t, lhs, "!=", rhs)
        return False

    elif isinstance(lhs, list):
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


def only_firstone(l, condition):
    found = False
    for i, e in reversed(list(enumerate(l))):
        if condition(e):
            if found:
                del l[i]
            found = True


def unique_by(l, key):
    return list({key(e): e for e in l}.values())
