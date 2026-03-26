# pysource-codegen thinks that the this ast is valid python code, but this is not the case:
from ast import AnnAssign
from ast import Constant
from ast import Load
from ast import Module
from ast import Starred
from ast import Store
from ast import Subscript
from ast import Tuple
tree = Module(
  body=[
    AnnAssign(
      target=Subscript(
        value=Constant(value=0),
        slice=Tuple(
          elts=[
            Starred(
              value=Constant(value=0),
              ctx=Load())],
          ctx=Load()),
        ctx=Store()),
      annotation=Constant(value=0),
      simple=0)])

# version: 3.14.3
# seed = 4054875342
#
# exception during `compile(ast.unparse(tree))`:
# can't use starred expression here (<file>, line 1)Source:
# 0[*0,]: 0
#
