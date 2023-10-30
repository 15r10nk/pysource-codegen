from ast import Invert
from ast import Load
from ast import Module
from ast import Name
from ast import Pass
from ast import UnaryOp
from ast import With
from ast import withitem

tree = Module(
    body=[
        With(
            items=[
                withitem(
                    context_expr=Name(id="name_2", ctx=Load()),
                    optional_vars=UnaryOp(
                        op=Invert(), operand=Name(id="something", ctx=Load())
                    ),
                )
            ],
            body=[Pass()],
        )
    ],
    type_ignores=[],
)

# version: 3.12.0
#
# Source:
# with name_2 as ~something:
#     pass
#
#
# Error:
#     SyntaxError('cannot assign to expression', ('<file>', 1, 16, 'with name_2 as ~something:\n', 1, 26))
