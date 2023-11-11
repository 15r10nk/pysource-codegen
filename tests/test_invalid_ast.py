import ast
import hashlib
import sys
import textwrap
from pathlib import Path

import pytest
from pysource_minimize._minimize import minimize_ast

from pysource_codegen._codegen import generate_ast
from pysource_codegen._codegen import is_valid_ast
from pysource_codegen._codegen import unparse

sample_dir = Path(__file__).parent / "invalid_ast_samples"
sample_dir.mkdir(exist_ok=True)


def does_compile(tree: ast.AST):
    for node in ast.walk(tree):
        if isinstance(node, ast.BoolOp) and len(node.values) < 2:
            return False
        if not isinstance(node, ast.JoinedStr) and any(
            isinstance(n, ast.FormattedValue) for n in ast.iter_child_nodes(node)
        ):
            return False
    try:
        source = unparse(tree)
        compile(source, "<file>", "exec")
    except:
        return False
    return True


@pytest.mark.parametrize(
    "file", [pytest.param(f, id=f.stem[:12]) for f in sample_dir.glob("*.py")]
)
def test_invalid_ast(file):
    code = file.read_text()
    print(code)
    globals = {}
    try:
        exec(code, globals)
    except (NameError, ImportError) as e:
        pytest.skip(f"wrong python version {e}")

    tree = globals["tree"]

    for node in ast.walk(tree):
        for field in node._fields:
            if not hasattr(node, field):
                pytest.skip(
                    f"wrong python version {node.__class__.__name__} is missing .{field}"
                )
        if sys.version_info < (3, 8) and isinstance(node, ast.Constant):
            pytest.skip(f"ast.Constant can not be unparsed on python3.7")

    assert is_valid_ast(tree) == does_compile(tree)


def test_generate():
    generate_invalid_ast(0)


def generate_invalid_ast(seed):
    print("seed=", seed)

    tree = generate_ast(seed)

    if not does_compile(tree):
        assert is_valid_ast(tree)

        def checker(tree):
            return not does_compile(tree) and is_valid_ast(tree)

        new_tree = minimize_ast(tree, checker)

        print(
            "pysource-codegen thinks that the current ast produces valid python code, but this is not the case:"
        )
        info = "from ast import *\n"
        info += f"tree = {ast.dump(new_tree,**(dict(indent=2) if sys.version_info >=(3,9) else {}))}\n"
        source = ""
        try:
            source = unparse(new_tree)
            compile(source, "<file>", "exec")
        except Exception as e:
            comment = f"version: {sys.version.split()[0]}\n\n"
            if source:
                comment += f"Source:\n{source}\n\n"
            comment += f"\nError:\n    {e!r}"

            info += "\n" + textwrap.indent(comment, "# ", lambda l: True)

            print(info)
            name = sample_dir / f"{hashlib.sha256(info.encode('utf-8')).hexdigest()}.py"
            name.write_text(info)
            return True
        else:
            assert False
    return False
