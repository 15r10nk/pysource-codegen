from ast import Load
from ast import Module
from ast import Name
from ast import NamedExpr
from ast import Store
from ast import TypeAlias

tree = Module(
    body=[
        TypeAlias(
            name=Name(id="name_0", ctx=Store()),
            value=NamedExpr(
                target=Name(id="name_2", ctx=Store()),
                value=Name(id="name_0", ctx=Load()),
            ),
        )
    ]
)

# version: 3.13.0b1
# seed = 1933771
#
# Source:
# type name_0 = (name_2 := name_0)
#
#
# Error:
#     SyntaxError('named expression cannot be used within a type alias')
