# pysource-codegen thinks that the this ast is valid python code, but this is not the case:
from ast import arguments
from ast import Await
from ast import comprehension
from ast import Constant
from ast import Expr
from ast import GeneratorExp
from ast import Lambda
from ast import Module
from ast import Name
from ast import Store
tree = Module(
  body=[
    Expr(
      value=GeneratorExp(
        elt=Constant(value=0),
        generators=[
          comprehension(
            target=Name(id='unique_name_0', ctx=Store()),
            iter=Constant(value=0),
            ifs=[
              Await(
                value=Lambda(
                  args=arguments(
                    posonlyargs=[],
                    args=[],
                    kwonlyargs=[],
                    kw_defaults=[],
                    defaults=[]),
                  body=Constant(value=0)))],
            is_async=0)]))],
  type_ignores=[])

# version: 3.12.12
# seed = 840948434
#
# Source:
# (0 for unique_name_0 in 0 if (await lambda: 0))
#
#
