from ast import Constant
from ast import For
from ast import Load
from ast import Module
from ast import Name
from ast import Pass
from ast import Set
from ast import Store
from ast import Tuple

tree = Module(
    body=[
        For(
            target=Tuple(elts=[Set(elts=[Name(id="name_3", ctx=Load())])], ctx=Store()),
            iter=Constant(value=1),
            body=[Pass()],
            orelse=[],
        )
    ],
    type_ignores=[],
)

# version: 3.12.0
#
# Source:
# for {name_3}, in 1:
#     pass
#
#
# Error:
#     SyntaxError('cannot assign to set display', ('<file>', 1, 5, 'for {name_3}, in 1:\n', 1, 13))
