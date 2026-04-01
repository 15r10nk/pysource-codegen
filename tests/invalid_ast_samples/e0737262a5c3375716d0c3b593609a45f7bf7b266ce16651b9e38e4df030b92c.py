# pysource-codegen thinks that the this ast is valid python code, but this is not the case:
from ast import *
tree = Module(body=[Expr(value=GeneratorExp(elt=DictComp(key=Constant(value=0, kind=None), value=Constant(value=0, kind=None), generators=[comprehension(target=List(elts=[], ctx=Store()), iter=Tuple(elts=[], ctx=Load()), ifs=[Await(value=Constant(value=0, kind=None))], is_async=0)]), generators=[comprehension(target=Name(id='unique_name_0', ctx=Store()), iter=Constant(value=0, kind=None), ifs=[], is_async=0)]))], type_ignores=[])

# version: 3.8.20
# seed = 5927773876
# 
# exception during `compile(ast.unparse(tree))`:
# asynchronous comprehension outside of an asynchronous function (<file>, line 0)Source:
# 
# ({0: 0 for [] in () if (await 0)} for unique_name_0 in 0)
# 
# 
