# pysource-codegen thinks that the this ast is valid python code, but this is not the case:
from ast import Await
from ast import Compare
from ast import comprehension
from ast import Constant
from ast import Expr
from ast import GeneratorExp
from ast import GtE
from ast import Module
from ast import Store
from ast import Tuple
tree = Module(
  body=[
    Expr(
      value=GeneratorExp(
        elt=Constant(value=0),
        generators=[
          comprehension(
            target=Tuple(elts=[], ctx=Store()),
            iter=Constant(value=0),
            ifs=[
              Await(
                value=Compare(
                  left=Constant(value=0),
                  ops=[
                    GtE()],
                  comparators=[
                    Constant(value=0)]))],
            is_async=1)]))],
  type_ignores=[])

# version: 3.12.12
# seed = 4282596960
#
# tree.body[0].value.generators[0].ifs[0]: Compare(
#   left=Await(
#     value=Constant(value=0)),
#   ops=[
#     GtE()],
#   comparators=[
#     Constant(value=0)]) != Await(
#   value=Compare(
#     left=Constant(value=0),
#     ops=[
#       GtE()],
#     comparators=[
#       Constant(value=0)]))Source:
# (0 async for () in 0 if (await 0 >= 0))
#
#
