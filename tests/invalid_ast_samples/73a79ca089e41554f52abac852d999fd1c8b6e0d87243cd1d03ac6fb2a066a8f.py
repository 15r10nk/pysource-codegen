from ast import Assign
from ast import Constant
from ast import Load
from ast import Module
from ast import Name

tree = Module(
    body=[Assign(targets=[Constant(value=True)], value=Name(id="name_4", ctx=Load()))],
    type_ignores=[],
)

# version: 3.12.0
#
# Source:
# True = name_4
#
#
# Error:
#     SyntaxError('cannot assign to True', ('<file>', 1, 1, 'True = name_4\n', 1, 5))
