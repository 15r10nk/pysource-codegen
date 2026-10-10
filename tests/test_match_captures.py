import ast
import sys
import unittest

from pysource_codegen._codegen import is_valid_ast


@unittest.skipUnless(sys.version_info >= (3, 10), "requires pattern matching")
class TestMatchCaptures(unittest.TestCase):
    def test_captures_can_be_distributed_across_children(self):
        for pattern in (
            "C(0, value=x)",
            "[0, x, y]",
            "[x, y] as z",
            "{'a': x, 'b': y, **z}",
            "[x, y] | C(y, value=x)",
        ):
            with self.subTest(pattern=pattern):
                tree = ast.parse(f"match subject:\n    case {pattern}: pass\n")
                compile(tree, "<test>", "exec")
                self.assertTrue(is_valid_ast(tree))

    def test_duplicate_or_inconsistent_captures_are_rejected(self):
        for pattern in ("[x, x]", "C(x, value=x)", "[x] | [y]"):
            with self.subTest(pattern=pattern):
                tree = ast.parse(f"match subject:\n    case {pattern}: pass\n")
                with self.assertRaises(SyntaxError):
                    compile(tree, "<test>", "exec")
                self.assertFalse(is_valid_ast(tree))
