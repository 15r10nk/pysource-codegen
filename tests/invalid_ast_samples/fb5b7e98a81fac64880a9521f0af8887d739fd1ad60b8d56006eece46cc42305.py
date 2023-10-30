from ast import Module
from ast import Return

tree = Module(body=[Return()], type_ignores=[])

# version: 3.12.0
#
# Source:
# return
#
#
# Error:
#     SyntaxError("'return' outside function", ('<file>', 1, 1, None, 1, 7))
