from ast import Break
from ast import Module

tree = Module(body=[Break()], type_ignores=[])

# Source:
# break
# Error:
#     SyntaxError("'break' outside loop", ('<file>', 1, 1, None, 1, 6))
