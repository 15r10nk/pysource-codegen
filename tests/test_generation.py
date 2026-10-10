import ast
import sys
import unittest

from pysource_codegen._codegen import generate_ast
from pysource_codegen._codegen import is_valid_ast
from pysource_codegen._limits import template_not_equal_parser_bug


class TestGeneration(unittest.TestCase):
    def test_match_or_final_match_as_can_be_wildcard(self):
        generate_ast(7327709108, depth_limit=9)

    @unittest.skipUnless(sys.version_info >= (3, 14), "requires template strings")
    def test_template_not_equal_format_spec_matches_runtime_parser(self):
        tree = ast.parse("t'{0 != 0:}'")
        interpolation = tree.body[0].value.values[0]
        interpolation.str = "0 != 0"
        self.assertEqual(is_valid_ast(tree), not template_not_equal_parser_bug)
