from ast import Expr
from ast import FormattedValue
from ast import Load
from ast import Module
from ast import Name

tree = Module(
    body=[
        Expr(value=FormattedValue(value=Name(id="name_1", ctx=Load()), conversion=115))
    ],
    type_ignores=[],
)

# version: 3.12.0
#
# Source:
# {name_1!s}
#
#
# Error:
#     SyntaxError('invalid syntax', ('<file>', 1, 8, '{name_1!s}\n', 1, 9))
