# pysource-codegen thinks that the this ast is valid python code, but this is not the case:
from ast import *
tree = Module(
  body=[
    ClassDef(
      name='name_3',
      bases=[],
      keywords=[],
      body=[
        FunctionDef(
          name='name_4',
          args=arguments(
            posonlyargs=[],
            args=[],
            kwonlyargs=[],
            kw_defaults=[],
            defaults=[]),
          body=[
            Pass()],
          decorator_list=[],
          returns=DictComp(
            key=Constant(value=0),
            value=Constant(value=0),
            generators=[
              comprehension(
                target=Name(id='unique_name_17', ctx=Store()),
                iter=Name(id='unique_name_18', ctx=Load()),
                ifs=[],
                is_async=0)]),
          type_params=[
            TypeVarTuple(name='name_1')])],
      decorator_list=[],
      type_params=[])],
  type_ignores=[])

# version: 3.12.12
# seed = 2936434838
# 
# exception during `compile(ast.unparse(tree))`:
# Cannot use comprehension in annotation scope within class scope (<file>, line 3)Source:
# class name_3:
# 
#     def name_4[*name_1]() -> {0: 0 for unique_name_17 in unique_name_18}:
#         pass
# 
