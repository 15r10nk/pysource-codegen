from ast import JoinedStr
from ast import Load
from ast import Module
from ast import Name
from ast import TypeAlias

tree = Module(
    body=[
        TypeAlias(
            name=JoinedStr(values=[]),
            type_params=[],
            value=Name(id="name_5", ctx=Load()),
        )
    ],
    type_ignores=[],
)

# version: 3.12.0
#
# Source:
# type f'' = name_5
#
#
# Error:
#     SyntaxError('invalid syntax', ('<file>', 1, 6, "type f'' = name_5\n", 1, 8))
