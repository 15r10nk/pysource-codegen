# pysource-codegen thinks that the this ast is valid python code, but this is not the case:
from ast import arguments
from ast import Constant
from ast import Expr
from ast import FormattedValue
from ast import JoinedStr
from ast import Lambda
from ast import Module
tree = Module(
  body=[
    Expr(
      value=JoinedStr(
        values=[
          FormattedValue(
            value=Lambda(
              args=arguments(
                posonlyargs=[],
                args=[],
                kwonlyargs=[],
                kw_defaults=[],
                defaults=[]),
              body=Constant(value=0)),
            conversion=-1)]))],
  type_ignores=[])

# version: 3.12.12
# seed = 4956199596
#
# Source:
# f'{lambda: 0}'
#
#
