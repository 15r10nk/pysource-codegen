# pysource-codegen thinks that the this ast is valid python code, but this is not the case:
from ast import alias
from ast import ImportFrom
from ast import Module
tree = Module(
  body=[
    ImportFrom(
      module='name_3',
      names=[
        alias(name='name_0')])])

# version: 3.14.3
# seed = 8053535216
#
# Source:
# from name_3 import name_0
#
