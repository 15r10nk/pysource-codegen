# pysource-codegen thinks that the this ast is valid python code, but this is not the case:
from ast import Constant
from ast import Expr
from ast import FormattedValue
from ast import JoinedStr
from ast import Module
tree = Module(
  body=[
    Expr(
      value=JoinedStr(
        values=[
          FormattedValue(
            value=JoinedStr(
              values=[
                Constant(value='\\')]),
            conversion=-1)]))],
  type_ignores=[])

# version: 3.11.14
# seed = 4975514640
#
#
# Error during unparse:
#     ValueError('Unable to avoid backslash in f-string expression part')
