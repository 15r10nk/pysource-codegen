import ast
import hashlib
import sys
import textwrap
import unittest
import warnings
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent / "pysource-minimize" / "src"))

from pysource_codegen._codegen import generate_ast
from pysource_codegen._codegen import is_valid_ast
from pysource_codegen._codegen import unparse
from pysource_codegen._utils import ast_dump
from pysource_minimize._minimize import minimize_ast

sample_dir = Path(__file__).parent / "invalid_ast_samples"
sample_dir.mkdir(exist_ok=True)


class TestInvalidAst(unittest.TestCase):

    def setUp(self):
        self.details = []
        super().setUp()

    def addDetail(self, text):
        if hasattr(self, "details"):
            self.details.append(text)

    def does_compile(self, tree: ast.Module):
        for node in ast.walk(tree):
            if isinstance(node, ast.BoolOp) and len(node.values) < 2:
                return False
            if not isinstance(node, ast.JoinedStr) and any(
                isinstance(n, ast.FormattedValue) for n in ast.iter_child_nodes(node)
            ):
                return False
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", SyntaxWarning)
                source = unparse(tree)
                compile(source, "<file>", "exec")
                compile(ast.fix_missing_locations(tree), "<file>", "exec")
        except Exception as e:
            self.addDetail("exception during `compile(ast.unparse(tree))`:\n" + str(e))
            return False
        return True


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
            is_valid_ast(tree),
            self.does_compile(tree),
            msg="detailed info:\n" + "\n\n".join(self.details),
        )

    setattr(TestInvalidAst, "test_" + name, test_invalid_ast)


for file in sample_dir.glob("*.py"):
    gen_test(file.stem, file)


def x_test_example():
    seed = 2273381
    tree = generate_ast(seed)
    tree = generate_ast(seed, depth_limit=9)
    # print(ast.dump(tree, indent=2))
    assert is_valid_ast(tree)


def generate_invalid_ast(seed):
    print("seed =", seed)

    tree = generate_ast(seed, depth_limit=9)
    try:
        assert is_valid_ast(tree)
    except:
        print(f"error for is_valid_ast seed={seed}")
        raise

    if not does_compile(tree):
        last_checked_tree = tree

        def checker(tree):
            nonlocal last_checked_tree

            bug_found = not does_compile(tree) and is_valid_ast(tree)
            if bug_found:
                last_checked_tree = tree

            return bug_found

        try:
            new_tree = minimize_ast(tree, checker)
        except:
            print(f"error happend while minimize_ast seed={seed}")
            print(ast_dump(last_checked_tree))
            raise

        print(
            "pysource-codegen thinks that the current ast produces valid python code, but this is not the case:"
        )
        info = "from ast import *\n"
        info += f"tree = {ast_dump(new_tree)}\n"
        source = ""
        try:
            source = unparse(new_tree)
            compile(source, "<file>", "exec")
            compile(ast.fix_missing_locations(tree), "<file>", "exec")
        except Exception as e:
            comment = f"version: {sys.version.split()[0]}\nseed = {seed}\n\n"
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


if __name__ == "__main__":
    for i in range(0, 1000):
        if generate_invalid_ast(i):
            break
