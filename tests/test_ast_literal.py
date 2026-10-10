import ast
import copy

from pysource_codegen._utils import ast_literal


def test_ast_literal_keeps_keyword_arg_none():
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

    assert "arg=None" in literal

    namespace = {}
    exec("from ast import *\ntree = " + literal, namespace)

    keyword = namespace["tree"].body[0].value.keywords[0]
    assert keyword.__dict__["arg"] is None
    copy.deepcopy(keyword)


def test_ast_literal_omits_missing_required_fields():
    node = ast.AnnAssign.__new__(ast.AnnAssign)
    node.target = ast.Name(id="x", ctx=ast.Store())
    node.annotation = ast.Name(id="int", ctx=ast.Load())

    literal = ast_literal(node)

    assert "simple=" not in literal
