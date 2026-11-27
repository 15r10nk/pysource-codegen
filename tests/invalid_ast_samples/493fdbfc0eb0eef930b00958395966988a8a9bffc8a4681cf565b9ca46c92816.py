from ast import alias
from ast import arguments
from ast import FunctionDef
from ast import ImportFrom
from ast import Module

lazy_import = ImportFrom(names=[alias(name="name_1")], level=1)
lazy_import.is_lazy = 5
tree = Module(
    body=[FunctionDef(name="name_1", args=arguments(), body=[lazy_import], lineno=1)]
)

# version: 3.15.1
# seed = 8
#
# Source:
# def name_1():
#     lazy from . import name_1
#
#
# Error:
#     SyntaxError('lazy from ... import not allowed inside functions')
