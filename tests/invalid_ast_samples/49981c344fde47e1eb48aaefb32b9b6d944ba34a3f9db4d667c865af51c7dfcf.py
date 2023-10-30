from ast import Load
from ast import Module
from ast import Name
from ast import NamedExpr
from ast import TypeAlias

tree = Module(
    body=[
        TypeAlias(
            name=Name(id="name_0", ctx=Load()),
            type_params=[],
            value=NamedExpr(
                target=Name(id="name_2", ctx=Load()),
                value=Name(id="name_5", ctx=Load()),
            ),
        )
    ],
    type_ignores=[],
)

# version: 3.12.0
#
# Source:
# type name_0 = (name_2 := name_5)
#
#
# Error:
#     SyntaxError('named expression cannot be used within a type alias')
