from ast import Constant
from ast import Dict
from ast import Expr
from ast import JoinedStr
from ast import Load
from ast import Module
from ast import Name
from ast import NamedExpr

tree = Module(
    body=[
        Expr(
            value=NamedExpr(
                target=Dict(
                    keys=[],
                    values=[
                        JoinedStr(values=[Constant(value="text")]),
                        Constant(value=""),
                    ],
                ),
                value=Name(id="something", ctx=Load()),
            )
        )
    ],
    type_ignores=[],
)

# version: 3.12.0
#
# Source:
# ({} := something)
#
#
# Error:
#     SyntaxError('cannot use assignment expressions with dict literal', ('<file>', 1, 2, '({} := something)\n', 1, 4))
