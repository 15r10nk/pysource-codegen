# pysource-codegen thinks that the this ast is valid python code, but this is not the case:
from ast import arguments
from ast import AsyncFunctionDef
from ast import Await
from ast import comprehension
from ast import Constant
from ast import FunctionDef
from ast import ListComp
from ast import Module
from ast import Name
from ast import Pass
from ast import Store
tree = Module(
  body=[
    AsyncFunctionDef(
      name='name_2',
      args=arguments(),
      body=[
        FunctionDef(
          name='name_0',
          args=arguments(),
          body=[
            Pass()],
          returns=ListComp(
            elt=Await(
              value=Constant(value=0)),
            generators=[
              comprehension(
                target=Name(id='unique_name_0', ctx=Store()),
                iter=Constant(value=0),
                is_async=0)]))])])

# version: 3.14.3
# seed = 2437485028
#
# exception during `compile(ast.unparse(tree))`:
# asynchronous comprehension outside of an asynchronous function (<file>, line 3)Source:
# async def name_2():
#
#     def name_0() -> [await 0 for unique_name_0 in 0]:
#         pass
#
