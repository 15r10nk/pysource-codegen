from ast import Assign
from ast import Constant
from ast import JoinedStr
from ast import Module
from ast import Store
from ast import Tuple

tree = Module(
    body=[
        Assign(
            targets=[Tuple(elts=[JoinedStr(values=[])], ctx=Store())],
            value=Constant(value=False),
        )
    ],
    type_ignores=[],
)

# version: 3.12.0
#
# Source:
# f'', = False
#
#
# Error:
#     SyntaxError('cannot assign to f-string expression', ('<file>', 1, 1, "f'', = False\n", 1, 4))
