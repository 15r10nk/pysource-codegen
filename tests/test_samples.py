import ast
import unittest
import warnings
from pathlib import Path
from typing import Callable

from ._validation import is_valid_python
from pysource_codegen._codegen import is_valid_ast


def load_source(file: Path) -> ast.Module:
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", SyntaxWarning)
            return ast.parse(file.read_text(), filename=str(file))
    except SyntaxError as error:
        # A source feature unavailable on this interpreter has no AST to replay.
        raise unittest.SkipTest(
            f"Source cannot be parsed on this Python: {error}"
        ) from error


def load_ast(file: Path) -> ast.Module:
    namespace: dict = {}
    try:
        # AST fixtures construct trees; the represented program is not executed.
        exec(compile(file.read_text(), str(file), "exec", dont_inherit=True), namespace)
    except (ImportError, NameError) as error:
        raise unittest.SkipTest(
            f"AST node unavailable on this Python: {error}"
        ) from error
    tree = namespace["tree"]
    if not isinstance(tree, ast.Module):
        raise TypeError(f"AST sample must define a Module: {file}")
    return tree


class TestSamples(unittest.TestCase):
    """Directory names record where samples came from, not their expected validity."""


def add_sample(file: Path, loader: Callable[[Path], ast.Module]) -> None:
    def test_sample(self: TestSamples) -> None:
        tree = loader(file)
        details = [str(file), file.read_text()]

        def add_detail(*items: object) -> None:
            details.append(" ".join(map(str, items)))

        expected = is_valid_python(tree, add_detail)
        accepted = is_valid_ast(tree, add_detail)
        self.assertEqual(accepted, expected, "\n\n".join(details))

    name = f"test_{file.parent.name}_{file.stem}"
    setattr(TestSamples, name, test_sample)


for directory, loader in (
    ("valid_source_samples", load_source),
    ("invalid_ast_samples", load_ast),
):
    files = sorted((Path(__file__).parent / directory).glob("*.py"))
    if not files:
        raise RuntimeError(f"No samples found in {directory}")
    for file in files:
        add_sample(file, loader)
