from ast import Dict
from ast import Expr
from ast import Load
from ast import Module
from ast import Name

tree = Module(
    body=[
        Expr(
            value=Dict(
                keys=[
                    Name(id="name_5", ctx=Load()),
                    Name(id="name_5", ctx=Load()),
                    Name(id="name_4", ctx=Load()),
                    Name(id="name_3", ctx=Load()),
                ],
                values=[],
            )
        )
    ],
    type_ignores=[],
)

# version: 3.12.0
# seed = 4378073
#
# Source:
# {}
#
#
# Error:
#     ValueError("Dict doesn't have the same number of keys as values")
