from ast import alias
from ast import ExceptHandler
from ast import Import
from ast import Module
from ast import Pass
from ast import Try

lazy_import = Import(names=[alias(name="name_4")])
lazy_import.is_lazy = 5
tree = Module(
    body=[
        Try(
            body=[lazy_import],
            handlers=[ExceptHandler(body=[Pass()])],
        )
    ]
)

# version: 3.15.1
# seed = 19
#
# Source:
# try:
#     lazy import name_4
# except:
#     pass
#
#
# Error:
#     SyntaxError('lazy import not allowed inside try/except blocks')
