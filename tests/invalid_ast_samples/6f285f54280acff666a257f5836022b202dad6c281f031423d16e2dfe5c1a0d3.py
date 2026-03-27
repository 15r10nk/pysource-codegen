# pysource-codegen thinks that the this ast is valid python code, but this is not the case:
from ast import Constant
from ast import Expr
from ast import ExtSlice
from ast import Index
from ast import Load
from ast import Module
from ast import Subscript
tree = Module(body=[Expr(value=Subscript(value=Constant(value=0, kind=None), slice=ExtSlice(dims=[Index(value=Constant(value=0, kind=None))]), ctx=Load()))], type_ignores=[])

# version: 3.8.20
# seed = 5375064626
#
# tree.body[0].value.slice: Index(value=Constant(value=0, kind=None)) != ExtSlice(dims=[Index(value=Constant(value=0, kind=None))])Source:
#
# 0[0]
#
#
