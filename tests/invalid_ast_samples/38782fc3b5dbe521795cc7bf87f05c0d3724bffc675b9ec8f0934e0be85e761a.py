# pysource-codegen thinks that the this ast is valid python code, but this is not the case:
from ast import *
tree = Module(
  body=[
    Expr(
      value=JoinedStr(
        values=[
          FormattedValue(
            value=Dict(keys=[], values=[]),
            conversion=115,
            format_spec=JoinedStr(
              values=[
                Constant(value="'''")])),
          Constant(value='"""')]))],
  type_ignores=[])

# version: 3.9.25
# seed = 4818690854
# 
# Source:
# f'{ {}!s:'''}"""'
# 
