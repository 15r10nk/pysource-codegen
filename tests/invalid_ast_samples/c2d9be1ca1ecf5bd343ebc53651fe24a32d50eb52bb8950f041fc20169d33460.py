from ast import Expr
from ast import Module
from ast import Name
from ast import Starred
from ast import Store

tree = Module(
    body=[Expr(value=Starred(value=Name(id="name_1", ctx=Store()), ctx=Store()))],
    type_ignores=[],
)

# version: 3.12.0
#
# Source:
# *name_1
#
#
# Error:
#     SyntaxError("can't use starred expression here", ('<file>', 1, 1, None, 1, 8))
