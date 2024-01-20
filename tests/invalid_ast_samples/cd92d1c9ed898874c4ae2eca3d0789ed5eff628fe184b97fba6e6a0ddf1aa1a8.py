from ast import Assign
from ast import Load
from ast import Module
from ast import Name

tree = Module(
    body=[Assign(targets=[], value=Name(id="name_1", ctx=Load()))], type_ignores=[]
)

# version: 3.12.0
# seed = 2914913
#
# Source:
# name_1
#
#
# Error:
#     ValueError('empty targets on Assign')
