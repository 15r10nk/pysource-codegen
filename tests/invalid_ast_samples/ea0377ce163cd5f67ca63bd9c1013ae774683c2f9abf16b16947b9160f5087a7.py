# pysource-codegen thinks that the this ast is valid python code, but this is not the case:
from ast import *
tree = Module(
  body=[
    FunctionDef(
      name='name_1',
      args=arguments(),
      body=[
        While(
          test=Constant(value=0),
          body=[
            AnnAssign(
              target=Attribute(
                value=Constant(value=0),
                attr='name_1',
                ctx=Store()),
              annotation=Await(
                value=Constant(value=0)),
              value=YieldFrom(
                value=Constant(value=0)),
              simple=0)],
          orelse=[
            Return(
              value=Constant(value=0))])])])

# version: 3.13.12
# seed = 5638063302
# 
# exception during `compile(ast.unparse(tree))`:
# 'return' with value in async generator (<file>, line 5)Source:
# def name_1():
#     while 0:
#         0 .name_1: await 0 = (yield from 0)
#     else:
#         return 0
# 
