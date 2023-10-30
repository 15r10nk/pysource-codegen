from ast import Expr
from ast import Load
from ast import Module
from ast import Name
from ast import Slice

tree = Module(
    body=[
        Expr(
            value=Slice(
                lower=Name(id="name_0", ctx=Load()),
                upper=Name(id="name_2", ctx=Load()),
                step=Name(id="name_2", ctx=Load()),
            )
        )
    ],
    type_ignores=[],
)

# version: 3.12.0
#
# Source:
# name_0:name_2:name_2
#
#
# Error:
#     SyntaxError('invalid syntax', ('<file>', 1, 14, 'name_0:name_2:name_2\n', 1, 15))
