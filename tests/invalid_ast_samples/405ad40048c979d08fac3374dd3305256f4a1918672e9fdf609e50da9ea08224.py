from ast import Break
from ast import Module

tree = Module(body=[Break()], type_ignores=[])

# version: 3.12.0
#
# Source:
# break
#
#
# Error:
#     SyntaxError("'break' outside loop", ('<file>', 1, 1, None, 1, 6))
