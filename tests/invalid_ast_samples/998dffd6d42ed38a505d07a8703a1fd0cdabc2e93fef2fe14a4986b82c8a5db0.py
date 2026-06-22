# pysource-codegen thinks that the this ast is valid python code, but this is not the case:
from ast import BoolOp
from ast import Expr
from ast import Load
from ast import Module
from ast import Name
from ast import Or
from ast import Set
from ast import Starred
tree = Module(
  body=[
    Expr(
      value=Set(
        elts=[
          Starred(
            value=BoolOp(
              op=Or(),
              values=[
                Name(id='unique_name_0', ctx=Load()),
                Name(id='unique_name_1', ctx=Load())]),
            ctx=Load())]))],
  type_ignores=[])

# version: 3.12.12
# seed = 9361338776
#
# Source:
# {*unique_name_0 or unique_name_1}
#
#
