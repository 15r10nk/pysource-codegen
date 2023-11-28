from ast import ImportFrom
from ast import Module

tree = Module(body=[ImportFrom(module="name_5", names=[], level=0)], type_ignores=[])

# version: 3.9.15
# seed = 4634023
#
# Source:
# from name_5 import
#
#
# Error:
#     SyntaxError('invalid syntax', ('<file>', 1, 20, 'from name_5 import \n'))
