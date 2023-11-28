from ast import Import
from ast import Module

tree = Module(body=[Import(names=[])], type_ignores=[])

# version: 3.9.15
# seed = 4634023
#
# Source:
# import
#
#
# Error:
#     SyntaxError('invalid syntax', ('<file>', 1, 8, 'import \n'))
