# pysource-codegen thinks that the this ast is valid python code, but this is not the case:
from ast import Constant
from ast import Load
from ast import Module
from ast import Pass
from ast import Tuple
from ast import With
from ast import withitem
tree = Module(
  body=[
    With(
      items=[
        withitem(
          context_expr=Tuple(
            elts=[
              Constant(value=0)],
            ctx=Load()))],
      body=[
        Pass()])])

# version: 3.14.3
# seed = 3985572564
#
# tree.body[0].items[0].context_expr: Constant(value=0) != Tuple(
#   elts=[
#     Constant(value=0)],
#   ctx=Load())Source:
# with (0,):
#     pass
#
