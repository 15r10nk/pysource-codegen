from ast import Expr
from ast import Module
from ast import Set

tree = Module(body=[Expr(value=Set(elts=[]))], type_ignores=[])

# version: 3.8.16
# seed = 8492326
#
#
# Error:
#     AssertionError()
