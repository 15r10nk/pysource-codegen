# pysource-codegen thinks that the this ast is valid python code, but this is not the case:
from ast import Attribute
from ast import Await
from ast import comprehension
from ast import Constant
from ast import Expr
from ast import GeneratorExp
from ast import IfExp
from ast import Load
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
            target=Attribute(
              value=Constant(value=0),
              attr='name_3',
              ctx=Store()),
            iter=Name(id='unique_name_0', ctx=Load()),
            ifs=[
              Await(
                value=IfExp(
                  test=Constant(value=0),
                  body=Constant(value=0),
                  orelse=Constant(value=0)))],
            is_async=1)]))],
  type_ignores=[])

# version: 3.12.12
# seed = 459821048
#
# tree.body[0].value.generators[0].ifs[0]: IfExp(
#   test=Constant(value=0),
#   body=Await(
#     value=Constant(value=0)),
#   orelse=Constant(value=0)) != Await(
#   value=IfExp(
#     test=Constant(value=0),
#     body=Constant(value=0),
#     orelse=Constant(value=0)))Source:
# (0 async for (0).name_3 in unique_name_0 if (await 0 if 0 else 0))
#
#
