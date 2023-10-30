from ast import BoolOp
from ast import Expr
from ast import Load
from ast import Module
from ast import Name
from ast import NamedExpr
from ast import Or

tree = Module(
    body=[
        Expr(
            value=NamedExpr(
                target=BoolOp(op=Or(), values=[Name(id="name_1", ctx=Load())]),
                value=Name(id="something", ctx=Load()),
            )
        )
    ],
    type_ignores=[],
)

# version: 3.12.0
#
# Source:
# ((name_1) := something)
#
#
# Error:
#     SyntaxError('cannot use assignment expressions with name', ('<file>', 1, 3, '((name_1) := something)\n', 1, 9))
