# pysource-codegen thinks that the this ast is valid python code, but this is not the case:
from ast import AnnAssign
from ast import arguments
from ast import AsyncFunctionDef
from ast import Await
from ast import comprehension
from ast import Constant
from ast import DictComp
from ast import Module
from ast import Name
from ast import Store
tree = Module(
  body=[
    AsyncFunctionDef(
      name='name_5',
      args=arguments(),
      body=[
        AnnAssign(
          target=Name(id='unique_name_0', ctx=Store()),
          annotation=DictComp(
            key=Constant(value=0),
            value=Await(
              value=Constant(value=0)),
            generators=[
              comprehension(
                target=Name(id='unique_name_1', ctx=Store()),
                iter=Constant(value=0),
                is_async=0)]),
          simple=1)])])

# version: 3.14.3
# seed = 6106937922
#
# exception during `compile(ast.unparse(tree))`:
# asynchronous comprehension outside of an asynchronous function (<file>, line 2)Source:
# async def name_5():
#     unique_name_0: {0: await 0 for unique_name_1 in 0}
#
