from ast import arguments
from ast import Attribute
from ast import comprehension
from ast import Constant
from ast import FunctionDef
from ast import GeneratorExp
from ast import Module
from ast import Name
from ast import NamedExpr
from ast import Pass
from ast import Store
from ast import TypeVarTuple
tree = Module(
  body=[
    FunctionDef(
      name='name_1',
      args=arguments(),
      body=[
        Pass()],
      type_params=[
        TypeVarTuple(
          name='name_4',
          default_value=GeneratorExp(
            elt=NamedExpr(
              target=Name(id='unique_name_0', ctx=Store()),
              value=Constant(value=0)),
            generators=[
              comprehension(
                target=Attribute(
                  value=Constant(value=0),
                  attr='name_3',
                  ctx=Store()),
                iter=Constant(value=0),
                is_async=False)]))])])

# version: 3.14.3
# seed = 2285594520
#
# Source:
# def name_1[*name_4 = ((unique_name_0 := 0) for 0 .name_3 in 0)]():
#     pass
#
#
# Error:
#     SyntaxError('assignment expression within a comprehension cannot be used in a TypeVar bound')
