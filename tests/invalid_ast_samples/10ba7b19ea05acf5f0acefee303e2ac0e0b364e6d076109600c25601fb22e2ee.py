# pysource-codegen thinks that the this ast is valid python code, but this is not the case:
from ast import *
tree = Module(
  body=[
    FunctionDef(
      name='name_5',
      args=arguments(),
      body=[
        Expr(value=Yield()),
        Return(
          value=Constant(value=0)),
        AnnAssign(
          target=Attribute(
            value=Constant(value=0),
            attr='name_0',
            ctx=Store()),
          annotation=Await(
            value=Constant(value=0)),
          simple=0)])])

# version: 3.13.12
# seed = 8016817840
# 
# exception during `compile(ast.unparse(tree))`:
# 'return' with value in async generator (<file>, line 3)Source:
# def name_5():
#     yield
#     return 0
#     0 .name_0: await 0
# 
