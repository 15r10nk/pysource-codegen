from ast import ExceptHandler
from ast import Expr
from ast import Global
from ast import Module
from ast import Name
from ast import Pass
from ast import Store
from ast import Try

tree = Module(
    body=[
        Try(
            body=[Pass()],
            handlers=[ExceptHandler(body=[Global(names=["name_0"])])],
            orelse=[Expr(value=Name(id="name_0", ctx=Store()))],
            finalbody=[],
        )
    ],
    type_ignores=[],
)

# version: 3.9.15
# seed = 8315429
#
# Source:
# try:
#     pass
# except:
#     global name_0
# else:
#     name_0
#
#
# Error:
#     SyntaxError("name 'name_0' is used prior to global declaration")
