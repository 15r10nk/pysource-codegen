from ast import Load
from ast import Module
from ast import Name
from ast import Set
from ast import TypeAlias

tree = Module(
    body=[
        TypeAlias(
            name=Set(elts=[Name(id="name_1", ctx=Load())]),
            type_params=[],
            value=Name(id="name_3", ctx=Load()),
        )
    ],
    type_ignores=[],
)

# version: 3.12.0
#
# Source:
# type {name_1} = name_3
#
#
# Error:
#     SyntaxError('invalid syntax', ('<file>', 1, 6, 'type {name_1} = name_3\n', 1, 7))
