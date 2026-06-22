# pysource-codegen thinks that the this ast is valid python code, but this is not the case:
from ast import Constant
from ast import Expr
from ast import Load
from ast import Module
from ast import Not
from ast import Starred
from ast import Tuple
from ast import UnaryOp
tree = Module(
  body=[
    Expr(
      value=Tuple(
        elts=[
          Starred(
            value=UnaryOp(
              op=Not(),
              operand=Constant(value=0)),
            ctx=Load())],
        ctx=Load()))],
  type_ignores=[])

# version: 3.12.12
# seed = 8322802300
#
# Source:
# *not 0,
#
#
