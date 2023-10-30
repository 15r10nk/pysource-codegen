from ast import Expr
from ast import JoinedStr
from ast import Load
from ast import Module
from ast import Name

tree = Module(
    body=[Expr(value=JoinedStr(values=[Name(id="name_2", ctx=Load())]))],
    type_ignores=[],
)

# version: 3.12.0
#
#
# Error:
#     ValueError('Unexpected node inside JoinedStr, <ast.Name object at 0x7f839e5bbed0>')
