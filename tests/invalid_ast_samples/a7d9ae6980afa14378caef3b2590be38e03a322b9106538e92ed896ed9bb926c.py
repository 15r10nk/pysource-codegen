from ast import Module
from ast import Pass
from ast import With

tree = Module(body=[With(items=[], body=[Pass()])], type_ignores=[])

# version: 3.9.15
# seed = 4634023
#
# Source:
# with :
#     pass
#
#
# Error:
#     SyntaxError('invalid syntax', ('<file>', 1, 6, 'with :\n'))
