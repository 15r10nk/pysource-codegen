from ast import Expr
from ast import Module
from ast import Slice

tree = Module(body=[Expr(value=Slice())], type_ignores=[])

# version: 3.12.0
#
# Source:
# :
#
#
# Error:
#     SyntaxError('invalid syntax', ('<file>', 1, 1, ':\n', 1, 2))
