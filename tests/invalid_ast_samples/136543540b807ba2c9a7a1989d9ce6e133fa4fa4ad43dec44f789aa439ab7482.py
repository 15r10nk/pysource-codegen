# pysource-codegen thinks that the this ast is valid python code, but this is not the case:
from ast import arg
from ast import arguments
from ast import Constant
from ast import Expr
from ast import Lambda
from ast import Module
tree = Module(
  body=[
    Expr(
      value=Lambda(
        args=arguments(
          posonlyargs=[
            arg(arg='name_4')],
          args=[],
          kwonlyargs=[],
          kw_defaults=[],
          defaults=[
            Constant(value=0)]),
        body=Constant(value=0)))],
  type_ignores=[])

# version: 3.12.12
# seed = 8497743406
#
# tree.body[0].value.args.defaults: [] != [0: Constant(value=0)]Source:
# lambda name_4, /: 0
#
#
