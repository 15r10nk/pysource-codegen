from ast import *

tree = Module(body=[Delete(targets=[Yield()])], type_ignores=[])

# version: 3.12.0
#
# Source:
# del (yield)
#
#
# Error:
#     SyntaxError('cannot delete yield expression', ('<file>', 1, 6, 'del (yield)\n', 1, 11))
