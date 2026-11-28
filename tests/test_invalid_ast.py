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
from .TestBase import TestBase

sample_dir = Path(__file__).parent / "invalid_ast_samples"
sample_dir.mkdir(exist_ok=True)


class TestInvalidAst(TestBase):
    pass


does_compile = TestInvalidAst().does_compile


def gen_test(name, file):
    def test_invalid_ast(self):
        code = file.read_text()
        self.addDetail("code:\n```\n" + code + "\n```")
        globals = {}
        try:
            exec(code, globals)
        except (NameError, ImportError) as e:

            return  # pytest.skip(f"wrong python version {e}")

        tree = globals["tree"]

        for node in ast.walk(tree):
            for field in node._fields:
                if not hasattr(node, field):
                    return  # pytest.skip( f"wrong python version {node.__class__.__name__} is missing .{field}")
            if sys.version_info < (3, 8) and isinstance(node, ast.Constant):
                return  # pytest.skip(f"ast.Constant can not be unparsed on python3.7")

        self.assertEqual(
            is_valid_ast(tree, self.addDetail),
            self.does_compile(tree),
            msg=self.message(),
        )

    setattr(TestInvalidAst, "test_" + name, test_invalid_ast)


for file in sample_dir.glob("*.py"):
    gen_test(file.stem, file)


@dataclass
class AstIssue:
    """A generated module that its checker rejects or that fails compilation."""

    tree: ast.Module
    checker_accepts: bool
    compiles: bool


def probe_invalid_ast(seed: int) -> AstIssue | None:
    tree = generate_ast(seed, depth_limit=9)
    assert isinstance(tree, ast.Module)
    checker_accepts = is_valid_ast(tree)
    compiles = does_compile(tree)
    if checker_accepts and compiles:
        return None
    return AstIssue(tree, checker_accepts, compiles)


def minimize_invalid_ast(seed: int, issue: AstIssue) -> str:
    """Shrink the module while preserving both observed outcomes."""
    last_checked_tree = issue.tree

    def checker(tree: ast.AST) -> bool:
        nonlocal last_checked_tree

        if not isinstance(tree, ast.Module):
            return False
        # Keep checker rejections distinct from accepted, uncompilable trees.
        bug_found = (
            does_compile(tree) == issue.compiles
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
        info = "# The checker accepts this generated AST, but it does not compile.\n"
    else:
        info = "# The generator produced an AST rejected by its checker.\n"
    info += "from ast import *\n"
    info += f"tree = {ast_literal(new_tree)}\n"
    comment = ""
    comment += f"version: {sys.version.split()[0]}\nseed = {seed}\n\n"
    comment += (
        f"checker accepts: {issue.checker_accepts}\ncompiles: {issue.compiles}\n\n"
    )

    t = TestBase()
    t.setUp()

    assert t.does_compile(new_tree) == issue.compiles
    assert is_valid_ast(new_tree) == issue.checker_accepts

    comment += "\n".join(t.details)

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
