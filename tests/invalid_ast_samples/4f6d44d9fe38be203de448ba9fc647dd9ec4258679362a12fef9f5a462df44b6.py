# pysource-codegen thinks that the this ast is valid python code, but this is not the case:
from ast import *
tree = Module(
  body=[
    Expr(
      value=JoinedStr(
        values=[
          Constant(value='\'\'\'"""'),
          FormattedValue(
            value=JoinedStr(values=[]),
            conversion=114)]))],
  type_ignores=[])

# version: 3.11.14
# seed = 506113934
# 
# Source:
# f'''\'\'\'"""{f\'\'!r}'''
# 
