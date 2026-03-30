# pysource-codegen thinks that the this ast is valid python code, but this is not the case:
from ast import arg
from ast import arguments
from ast import Await
from ast import Constant
from ast import FunctionDef
from ast import Module
from ast import Pass
tree = Module(body=[FunctionDef(name='name_5', args=arguments(posonlyargs=[], args=[], vararg=None, kwonlyargs=[arg(arg='name_4', annotation=Await(value=Constant(value=0, kind=None)), type_comment=None)], kw_defaults=[Constant(value=0, kind=None)], kwarg=None, defaults=[]), body=[Pass()], decorator_list=[], returns=None, type_comment=None)], type_ignores=[])

# version: 3.8.20
# seed = 9363117460
#
# exception during `compile(ast.unparse(tree))`:
# 'await' outside function (<file>, line 3)Source:
#
#
# def name_5(*, name_4: (await 0)=0):
#     pass
#
#
