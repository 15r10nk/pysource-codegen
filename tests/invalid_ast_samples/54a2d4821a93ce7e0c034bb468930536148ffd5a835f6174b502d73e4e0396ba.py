from ast import alias
from ast import ClassDef
from ast import Import
from ast import Module

lazy_import = Import(names=[alias(name="name_0")])
lazy_import.is_lazy = 2
tree = Module(body=[ClassDef(name="name_4", body=[lazy_import])])

# version: 3.15.1
# seed = 0
#
# Source:
# class name_4:
#     lazy import name_0
#
#
# Error:
#     SyntaxError('lazy import not allowed inside classes')
