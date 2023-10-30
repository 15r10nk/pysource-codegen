from ast import Await
from ast import Expr
from ast import Load
from ast import Module
from ast import Name

tree = Module(
    body=[Expr(value=Await(value=Name(id="name_0", ctx=Load())))], type_ignores=[]
)

# version: 3.12.0
#
# Source:
# await name_0
#
#
# Error:
#     SyntaxError("'await' outside function", ('<file>', 1, 1, None, 1, 13))
