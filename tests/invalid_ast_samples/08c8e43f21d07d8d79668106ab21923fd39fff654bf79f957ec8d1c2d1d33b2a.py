from ast import Expr
from ast import Load
from ast import Module
from ast import Name
from ast import YieldFrom

tree = Module(
    body=[Expr(value=YieldFrom(value=Name(id="name_1", ctx=Load())))], type_ignores=[]
)

# version: 3.12.0
#
# Source:
# yield from name_1
#
#
# Error:
#     SyntaxError("'yield' outside function", ('<file>', 1, 1, None, 1, 18))
