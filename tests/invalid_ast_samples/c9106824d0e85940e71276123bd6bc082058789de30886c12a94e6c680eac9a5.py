from ast import Expr
from ast import ExtSlice
from ast import Load
from ast import Module
from ast import Name
from ast import Subscript

tree = Module(
    body=[
        Expr(
            value=Subscript(
                value=Name(id="name_1", ctx=Load()), slice=ExtSlice(dims=[]), ctx=Load()
            )
        )
    ],
    type_ignores=[],
)

# version: 3.8.16
# seed = 6348378
#
# Source:
#
# name_1[]
#
#
#
# Error:
#     SyntaxError('invalid syntax', ('<file>', 2, 8, 'name_1[]\n'))
