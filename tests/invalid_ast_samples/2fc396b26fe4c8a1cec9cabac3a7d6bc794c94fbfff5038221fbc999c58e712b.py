# pysource-codegen thinks that the this ast is valid python code, but this is not the case:
from ast import alias
from ast import ImportFrom
from ast import Module
tree = Module(
  body=[
    ImportFrom(
      module='name_2',
      names=[
        alias(name='name_4', asname='name_3')],
      level=0,
      is_lazy=2)])

# version: 3.15.0b2
# seed = 2008839874
#
# tree.body[0].is_lazy: 1 != 2Source:
# lazy from name_2 import name_4 as name_3
#
#
