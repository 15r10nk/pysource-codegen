from ast import Constant
from ast import Expr
from ast import JoinedStr
from ast import Module

tree = Module(
    body=[Expr(value=JoinedStr(values=[Constant(value=None)]))], type_ignores=[]
)

# version: 3.12.0
#
#
# Error:
#     ValueError('Unexpected node inside JoinedStr, <ast.Constant object at 0x7f18e0fc7a50>')
