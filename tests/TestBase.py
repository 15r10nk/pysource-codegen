import ast
import unittest
import warnings
from typing import List

from pysource_codegen._codegen import unparse


class TestBase(unittest.TestCase):

    details: List[str]

    def setUp(self) -> None:
        self.details = []
        super().setUp()

    def addDetail(self, *text: object) -> None:
        text_str = " ".join(map(str, text))
        if hasattr(self, "details"):
            self.details.append(text_str)

    def message(self) -> str:
        return "detailed info:\n" + "\n\n".join(self.details)

    def does_compile(self, tree: ast.Module) -> bool:
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
