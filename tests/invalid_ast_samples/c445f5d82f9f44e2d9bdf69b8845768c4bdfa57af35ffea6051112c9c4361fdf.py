from ast import alias
from ast import ImportFrom
from ast import Module

lazy_import = ImportFrom(module="x", names=[alias(name="*")], level=0)
lazy_import.is_lazy = 1
tree = Module(body=[lazy_import])

# version: 3.15.1
#
# Source:
# lazy from x import *
#
#
# Error:
#     SyntaxError('lazy from ... import * is not allowed')
