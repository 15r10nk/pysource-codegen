from ast import Expr
from ast import Load
from ast import Module
from ast import Name
from ast import Starred

tree = Module(
    body=[Expr(value=Starred(value=Name(id="name_0", ctx=Load()), ctx=Load()))],
    type_ignores=[],
)

# version: 3.12.0
#
# Source:
# *name_0
#
#
# Error:
#     SyntaxError("can't use starred expression here", ('<file>', 1, 1, None, 1, 8))
