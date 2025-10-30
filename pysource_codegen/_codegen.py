from __future__ import annotations

import ast
import warnings
from typing import Callable

from ._codegen_rules import StdGenerator
from ._utils import ast_dump
from ._utils import unparse


def is_valid_ast(
    tree: ast.AST, print: Callable[..., None] = lambda *args: None
) -> bool:
    generator = StdGenerator()
    return generator.is_valid_ast(tree, print)


def check(tree: ast.AST) -> None:
    for node in ast.walk(tree):
        if isinstance(node, ast.arguments):
            assert len(node.posonlyargs) + len(node.args) >= len(
                node.defaults
            ), ast_dump(node)
            assert len(node.kwonlyargs) == len(node.kw_defaults)


def generate_ast(
    seed: int,
    *,
    node_limit: int = 10000000,
    depth_limit: int = 8,
    root_node: str = "Module",
    generator_type: type[StdGenerator] = StdGenerator,
) -> ast.AST:
    generator = generator_type(seed, depth_limit=depth_limit, node_limit=node_limit)

    with warnings.catch_warnings():
        warnings.simplefilter("ignore", SyntaxWarning)
        tree = generator.generate(root_node)
        check(tree)

    ast.fix_missing_locations(tree)
    return tree


def generate(
    seed: int,
    *,
    node_limit: int = 10000000,
    depth_limit: int = 8,
    root_node: str = "Module",
) -> str:
    tree = generate_ast(
        seed, node_limit=node_limit, depth_limit=depth_limit, root_node=root_node
    )
    return unparse(tree)
