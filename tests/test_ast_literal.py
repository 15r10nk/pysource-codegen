import ast
import copy
import unittest

from pysource_codegen._utils import ast_literal


class TestAstLiteral(unittest.TestCase):
    def test_ast_literal_keeps_keyword_arg_none(self):
        tree = ast.Module(
            body=[
                ast.Expr(
                    value=ast.Call(
                        func=ast.Name(id="f", ctx=ast.Load()),
                        args=[],
                        keywords=[
                            ast.keyword(value=ast.Name(id="x", ctx=ast.Load())),
                        ],
                    )
                )
            ],
            type_ignores=[],
        )

        literal = ast_literal(tree)

        self.assertIn("arg=None", literal)

        namespace = {}
        exec("from ast import *\ntree = " + literal, namespace)

        keyword = namespace["tree"].body[0].value.keywords[0]
        self.assertIsNone(keyword.__dict__["arg"])
        copy.deepcopy(keyword)

    def test_ast_literal_omits_missing_required_fields(self):
        node = ast.AnnAssign.__new__(ast.AnnAssign)
        node.target = ast.Name(id="x", ctx=ast.Store())
        node.annotation = ast.Name(id="int", ctx=ast.Load())

        literal = ast_literal(node)

        self.assertNotIn("simple=", literal)
