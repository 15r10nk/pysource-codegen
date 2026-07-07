# pysource-codegen thinks that the this ast is valid python code, but this is not the case:
from ast import alias
from ast import arguments
from ast import FunctionDef
from ast import ImportFrom
from ast import Module
tree = Module(
  body=[
    FunctionDef(
      name='name_5',
      args=arguments(),
      body=[
        ImportFrom(
          names=[
            alias(name='name_1')],
          level=1,
          is_lazy=1)])])

# version: 3.15.0b2
# seed = 8302950074
#
# exception during `compile(ast.unparse(tree))`:
# lazy from ... import not allowed inside functions (<file>, line 3)Source:
#
# def name_5():
#     lazy from . import name_1
#
#
