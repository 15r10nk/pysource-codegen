# pysource-codegen thinks that the this ast is valid python code, but this is not the case:
from ast import alias
from ast import Constant
from ast import ExceptHandler
from ast import Import
from ast import Module
from ast import Pass
from ast import TryStar
tree = Module(
  body=[
    TryStar(
      body=[
        Pass()],
      handlers=[
        ExceptHandler(
          type=Constant(value=0),
          body=[
            Pass()])],
      orelse=[
        Import(
          names=[
            alias(name='name_3', asname='name_2')],
          is_lazy=1)])])

# version: 3.15.0b3
# seed = 3304291040
#
# exception during `compile(ast.unparse(tree))`:
# lazy import not allowed inside try/except blocks (<file>, line 6)Source:
# try:
#     pass
# except* 0:
#     pass
# else:
#     lazy import name_3 as name_2
#
#
