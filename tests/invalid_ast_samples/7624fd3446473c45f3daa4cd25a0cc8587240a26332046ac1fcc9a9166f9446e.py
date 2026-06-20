# pysource-codegen thinks that the this ast is valid python code, but this is not the case:
from ast import Compare
from ast import Constant
from ast import Expr
from ast import Load
from ast import LtE
from ast import Module
from ast import Starred
from ast import Tuple
tree = Module(
  body=[
    Expr(
      value=Tuple(
        elts=[
          Starred(
            value=Compare(
              left=Constant(value=0),
              ops=[
                LtE()],
              comparators=[
                Constant(value=0)]),
            ctx=Load())],
        ctx=Load()))],
  type_ignores=[])

# version: 3.12.12
# seed = 4890780868
#
# Source:
# *0 <= 0,
#
#
