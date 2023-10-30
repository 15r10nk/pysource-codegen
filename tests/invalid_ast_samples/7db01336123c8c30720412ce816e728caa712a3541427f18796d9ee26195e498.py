from ast import And
from ast import AugAssign
from ast import BoolOp
from ast import Load
from ast import LShift
from ast import Module
from ast import Name

tree = Module(
    body=[
        AugAssign(
            target=BoolOp(
                op=And(),
                values=[Name(id="name_1", ctx=Load()), Name(id="name_4", ctx=Load())],
            ),
            op=LShift(),
            value=Name(id="name_0", ctx=Load()),
        )
    ],
    type_ignores=[],
)

# version: 3.12.0
#
# Source:
# name_1 and name_4 <<= name_0
#
#
# Error:
#     SyntaxError("'expression' is an illegal expression for augmented assignment", ('<file>', 1, 1, 'name_1 and name_4 <<= name_0\n', 1, 18))
