from ast import AugAssign
from ast import Load
from ast import MatMult
from ast import Module
from ast import Name
from ast import Store
from ast import Tuple

tree = Module(
    body=[
        AugAssign(
            target=Tuple(elts=[Name(id="something", ctx=Load())], ctx=Load()),
            op=MatMult(),
            value=Name(id="name_2", ctx=Store()),
        )
    ],
    type_ignores=[],
)

# version: 3.12.0
#
# Source:
# (something,) @= name_2
#
#
# Error:
#     SyntaxError("'tuple' is an illegal expression for augmented assignment", ('<file>', 1, 1, '(something,) @= name_2\n', 1, 13))
