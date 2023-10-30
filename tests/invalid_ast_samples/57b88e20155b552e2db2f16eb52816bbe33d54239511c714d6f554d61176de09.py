from ast import Expr
from ast import Module
from ast import Yield

tree = Module(body=[Expr(value=Yield())], type_ignores=[])

# version: 3.12.0
#
# Source:
# yield
#
#
# Error:
#     SyntaxError("'yield' outside function", ('<file>', 1, 1, None, 1, 6))
