# pysource-codegen thinks that the this ast is valid python code, but this is not the case:
from ast import AnnAssign
from ast import Constant
from ast import Module
from ast import Name
from ast import Store
tree = Module(
  body=[
    AnnAssign(
      target=Name(id='unique_name_0', ctx=Store()),
      annotation=Constant(value=0),
      simple=5)])

# version: 3.14.3
# seed = 1325708944
#
# Source:
# unique_name_0: 0
#
