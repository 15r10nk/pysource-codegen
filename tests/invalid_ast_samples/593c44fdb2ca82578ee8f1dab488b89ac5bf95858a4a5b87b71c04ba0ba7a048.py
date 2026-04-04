# pysource-codegen thinks that the this ast is valid python code, but this is not the case:
from ast import *
tree = Module(
  body=[
    Match(
      subject=Constant(value=0),
      cases=[
        match_case(
          pattern=MatchSequence(
            patterns=[
              MatchStar(name='name_5')]),
          body=[
            Global(
              names=[
                'name_5'])])])],
  type_ignores=[])

# version: 3.12.12
# seed = 812613440
# 
# exception during `compile(ast.unparse(tree))`:
# name 'name_5' is assigned to before global declaration (<file>, line 3)Source:
# match 0:
#     case [*name_5]:
#         global name_5
# 
