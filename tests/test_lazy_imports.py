import ast
import sys
import unittest

from pysource_codegen._codegen import generate
from pysource_codegen._codegen import is_valid_ast


@unittest.skipIf(sys.version_info < (3, 15), "lazy imports require Python 3.15")
class TestLazyImports(unittest.TestCase):
    def test_invalid_lazy_imports(self):
        for source in (
            "class C:\n    lazy import x",
            "def f():\n    lazy from x import y",
            "async def f():\n    lazy import x",
            "try:\n    lazy import x\nexcept Exception:\n    pass",
            "try:\n    pass\nexcept* Exception:\n    lazy from x import y",
            "lazy from x import *",
        ):
            with self.subTest(source=source):
                tree = ast.parse(source)
                with self.assertRaises(SyntaxError):
                    compile(tree, "<source>", "exec")
                self.assertFalse(is_valid_ast(tree))

    def test_lazy_future_import_is_not_generated(self):
        # The parser rejects this form before constructing an AST.
        tree = ast.parse("from __future__ import annotations")
        tree.body[0].is_lazy = 1
        with self.assertRaises(SyntaxError):
            ast.parse(ast.unparse(tree))
        self.assertFalse(is_valid_ast(tree))

    def test_valid_lazy_imports(self):
        for source in (
            "lazy import x",
            "lazy from . import y",
            "if condition:\n    lazy from x import y",
        ):
            with self.subTest(source=source):
                tree = ast.parse(source)
                compile(tree, "<source>", "exec")
                self.assertTrue(is_valid_ast(tree))

    def test_generated_source_compiles(self):
        # This seed used to emit a lazy import in class scope.
        compile(generate(0), "<generated>", "exec")
