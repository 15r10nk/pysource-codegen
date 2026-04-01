# pysource-codegen thinks that the this ast is valid python code, but this is not the case:
from ast import *
tree = Module(
  body=[
    Expr(
      value=JoinedStr(
        values=[
          Constant(value='\'\'\'"""'),
          FormattedValue(
            value=Name(id='unique_name_0', ctx=Load()),
            conversion=115),
          Constant(value="'")]))],
  type_ignores=[])

# version: 3.9.25
# seed = 4937944814
# 
# Source:
# f"\'\'\'"""{unique_name_0!s}'"
# 
