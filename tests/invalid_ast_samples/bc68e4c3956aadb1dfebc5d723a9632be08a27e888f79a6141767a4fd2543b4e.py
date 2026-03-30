# pysource-codegen thinks that the this ast is valid python code, but this is not the case:
from ast import AnnAssign
from ast import Attribute
from ast import Await
from ast import Constant
from ast import Module
from ast import Store
tree = Module(body=[AnnAssign(target=Attribute(value=Constant(value=0, kind=None), attr='name_4', ctx=Store()), annotation=Await(value=Constant(value=0, kind=None)), value=None, simple=0)], type_ignores=[])

# version: 3.8.20
# seed = 6814906850
#
# exception during `compile(ast.unparse(tree))`:
# 'await' outside function (<file>, line 2)Source:
#
# 0 .name_4: (await 0)
#
#
