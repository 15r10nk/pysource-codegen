from ast import Compare
from ast import Expr
from ast import Load
from ast import Lt
from ast import Module
from ast import Name

tree = Module(
    body=[
        Expr(
            value=Compare(
                left=Name(id="name_1", ctx=Load()),
                ops=[Lt()],
                comparators=[
                    Name(id="name_1", ctx=Load()),
                    Name(id="name_3", ctx=Load()),
                    Name(id="name_3", ctx=Load()),
                ],
            )
        )
    ],
    type_ignores=[],
)

# version: 3.12.0
# seed = 4378073
#
# Source:
# name_1 < name_1
#
#
# Error:
#     ValueError('Compare has a different number of comparators and operands')
