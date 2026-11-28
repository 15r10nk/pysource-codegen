from ast import alias
from ast import Constant
from ast import ExceptHandler
from ast import ImportFrom
from ast import Module
from ast import Pass
from ast import TryStar

lazy_import = ImportFrom(module="name_4", names=[alias(name="name_5")])
lazy_import.is_lazy = 1
tree = Module(
    body=[
        TryStar(
            body=[Pass()],
            handlers=[ExceptHandler(type=Constant(value=0), body=[lazy_import])],
        )
    ]
)

# version: 3.15.1
# seed = 14
#
# Source:
# try:
#     pass
# except* 0:
#     lazy from name_4 import name_5
#
#
# Error:
#     SyntaxError('lazy from ... import not allowed inside try/except blocks')
