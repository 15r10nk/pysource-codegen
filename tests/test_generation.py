import ast
import sys
import unittest
from unittest.mock import patch

from .test_valid_source import probe_valid_source
from pysource_codegen._codegen import is_valid_ast
from pysource_codegen._generator import Invalid
from pysource_codegen._limits import template_not_equal_parser_bug


class TestGeneration(unittest.TestCase):
    def test_probe_continues_after_infeasible_mutations(self):
        def generate_mutation(*args, generator_type, **kwargs):
            generator = generator_type()
            self.assertFalse(generator.use(False))
            decisions = [generator.use(), generator.use()]
            if not all(decisions):
                raise Invalid("Infeasible mutation")
            return ast.parse("pass")

        with patch(
            "tests.test_valid_source.generate_ast", side_effect=generate_mutation
        ) as generate:
            self.assertIsNone(probe_valid_source(0))
            self.assertEqual(generate.call_count, 3)
        with patch("tests.test_valid_source.generate_ast", side_effect=Invalid):
            with self.assertRaises(Invalid):
                probe_valid_source(0)

    @unittest.skipUnless(sys.version_info >= (3, 14), "requires template strings")
    def test_template_not_equal_format_spec_matches_runtime_parser(self):
        tree = ast.parse("t'{0 != 0:}'")
        interpolation = tree.body[0].value.values[0]
        interpolation.str = "0 != 0"
        self.assertEqual(is_valid_ast(tree), not template_not_equal_parser_bug)
