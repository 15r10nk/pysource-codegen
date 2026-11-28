from __future__ import annotations

import ast
import sys
import textwrap
from dataclasses import dataclass
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent / "pysource-minimize" / "src"))

from pysource_codegen._codegen import generate_ast
from pysource_codegen._codegen import is_valid_ast
from pysource_codegen._codegen import unparse
from pysource_codegen._utils import ast_dump
from pysource_codegen._utils import ast_literal
from pysource_minimize._minimize import minimize_ast

from ._validation import is_valid_python


@dataclass
class AstIssue:
    """A generated module that its checker rejects or that fails Python validation."""

    tree: ast.Module
    checker_accepts: bool
    valid_python: bool


def probe_invalid_ast(seed: int) -> AstIssue | None:
    tree = generate_ast(seed, depth_limit=9)
    assert isinstance(tree, ast.Module)
    checker_accepts = is_valid_ast(tree)
    valid_python = is_valid_python(tree)
    if checker_accepts and valid_python:
        return None
    return AstIssue(tree, checker_accepts, valid_python)


def minimize_invalid_ast(seed: int, issue: AstIssue) -> str:
    """Shrink the module while preserving both observed outcomes."""
    last_checked_tree = issue.tree

    def checker(tree: ast.AST) -> bool:
        nonlocal last_checked_tree

        if not isinstance(tree, ast.Module):
            return False
        # Keep checker rejections distinct from accepted, uncompilable trees.
        bug_found = (
            is_valid_python(tree) == issue.valid_python
            and is_valid_ast(tree) == issue.checker_accepts
        )
        if bug_found:
            last_checked_tree = tree

        return bug_found

    try:
        new_tree = minimize_ast(issue.tree, checker)
        assert isinstance(new_tree, ast.Module)
    except:
        print(f"error happend while minimize_ast seed={seed}")
        print(ast_dump(last_checked_tree))
        raise

    if issue.checker_accepts:
        info = "# The checker accepts this generated AST, but it fails compilation or AST round-trip.\n"
    else:
        info = "# The generator produced an AST rejected by its checker.\n"
    info += "from ast import *\n"
    info += f"tree = {ast_literal(new_tree)}\n"
    comment = ""
    comment += f"version: {sys.version.split()[0]}\nseed = {seed}\n\n"
    comment += f"checker accepts: {issue.checker_accepts}\nvalid_python: {issue.valid_python}\n\n"

    details: list[str] = []

    def add_detail(*items: object) -> None:
        details.append(" ".join(map(str, items)))

    assert is_valid_python(new_tree, add_detail) == issue.valid_python
    assert is_valid_ast(new_tree) == issue.checker_accepts

    comment += "\n".join(details)

    try:
        source = unparse(new_tree)
    except Exception as e:
        comment += f"\nError during unparse:\n    {e!r}"
    else:
        comment += f"Source:\n{source}\n\n"

    info += "\n" + textwrap.indent(comment, "# ", lambda l: True)

    return info


def generate_invalid_ast(seed):
    issue = probe_invalid_ast(seed)
    if issue is None:
        return False
    return minimize_invalid_ast(seed, issue)


if __name__ == "__main__":
    for i in range(0, 1000):
        if generate_invalid_ast(i):
            break
