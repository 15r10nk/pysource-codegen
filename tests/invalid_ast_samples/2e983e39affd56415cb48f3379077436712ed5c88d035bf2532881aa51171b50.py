# pysource-codegen thinks that the this ast is valid python code, but this is not the case:
from ast import Compare
from ast import Constant
from ast import Expr
from ast import Interpolation
from ast import JoinedStr
from ast import Module
from ast import NotEq
from ast import TemplateStr
tree = Module(
  body=[
    Expr(
      value=TemplateStr(
        values=[
          Interpolation(
            value=Compare(
              left=Constant(value=0),
              ops=[
                NotEq()],
              comparators=[
                Constant(value=0)]),
            str='0 != 0',
            conversion=-1,
            format_spec=JoinedStr())]))])

# version: 3.14.3
# seed = 4573685926
#
# Source:
# t'{0 != 0:}'
#
