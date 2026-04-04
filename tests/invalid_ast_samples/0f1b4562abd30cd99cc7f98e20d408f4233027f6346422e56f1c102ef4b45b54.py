# pysource-codegen thinks that the this ast is valid python code, but this is not the case:
from ast import *
tree = Module(
  body=[
    ClassDef(
      name='name_4',
      bases=[],
      keywords=[],
      body=[
        ClassDef(
          name='name_2',
          bases=[
            GeneratorExp(
              elt=Constant(value=0),
              generators=[
                comprehension(
                  target=Name(id='unique_name_0', ctx=Store()),
                  iter=Name(id='unique_name_1', ctx=Load()),
                  ifs=[],
                  is_async=0)])],
          keywords=[],
          body=[
            Pass()],
          decorator_list=[],
          type_params=[
            TypeVar(name='name_2')])],
      decorator_list=[],
      type_params=[])],
  type_ignores=[])

# version: 3.12.12
# seed = 2660269562
# 
# exception during `compile(ast.unparse(tree))`:
# Cannot use comprehension in annotation scope within class scope (<file>, line 3)Source:
# class name_4:
# 
#     class name_2[name_2]((0 for unique_name_0 in unique_name_1)):
#         pass
# 
