from ast import alias
from ast import arguments
from ast import AsyncFunctionDef
from ast import Import
from ast import Module

lazy_import = Import(names=[alias(name="x")])
lazy_import.is_lazy = 1
tree = Module(
    body=[AsyncFunctionDef(name="f", args=arguments(), body=[lazy_import], lineno=1)]
)

# version: 3.15.1
#
# Source:
# async def f():
#     lazy import x
#
#
# Error:
#     SyntaxError('lazy import not allowed inside functions')
