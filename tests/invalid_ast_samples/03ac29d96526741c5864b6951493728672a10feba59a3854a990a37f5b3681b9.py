# pysource-codegen thinks that the this ast is valid python code, but this is not the case:
from ast import Constant
from ast import Expr
from ast import JoinedStr
from ast import Module
tree = Module(
  body=[
    Expr(
      value=JoinedStr(
        values=[
          Constant(value="'", kind='u')]))])

# version: 3.14.3
# seed = 9058163422
#
# Source:
# f"'"
#
