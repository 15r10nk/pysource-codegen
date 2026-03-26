# pysource-codegen thinks that the this ast is valid python code, but this is not the case:
from ast import AnnAssign
from ast import arguments
from ast import AsyncFunctionDef
from ast import Attribute
from ast import Await
from ast import comprehension
from ast import Constant
from ast import List
from ast import Load
from ast import Module
from ast import Name
from ast import SetComp
from ast import Store
tree = Module(
  body=[
    AsyncFunctionDef(
      name='name_4',
      args=arguments(),
      body=[
        AnnAssign(
          target=Attribute(
            value=Constant(value=0),
            attr='name_4',
            ctx=Store()),
          annotation=SetComp(
            elt=Await(
              value=Constant(value=0)),
            generators=[
              comprehension(
                target=List(ctx=Store()),
                iter=Name(id='unique_name_0', ctx=Load()),
                is_async=0)]),
          simple=0)])])

# version: 3.14.3
# seed = 2246879344
#
# exception during `compile(ast.unparse(tree))`:
# asynchronous comprehension outside of an asynchronous function (<file>, line 1)
# can not compile annotation SetComp(elt=Await(value=Constant(value=0, kind=None)), generators=[comprehension(target=List(elts=[], ctx=Store(...)), iter=Name(id='unique_name_0', ctx=Load(...)), ifs=[], is_async=0)])Source:
# async def name_4():
#     0 .name_4: {await 0 for [] in unique_name_0}
#
