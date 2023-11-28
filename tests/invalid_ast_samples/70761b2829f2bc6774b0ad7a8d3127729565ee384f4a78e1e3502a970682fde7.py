from ast import Module
from ast import Pass
from ast import TryStar

tree = Module(
    body=[TryStar(body=[Pass()], handlers=[], orelse=[], finalbody=[])], type_ignores=[]
)

# version: 3.12.0
# seed = 3021191
#
# Source:
# try:
#     pass
#
#
# Error:
#     SyntaxError("expected 'except' or 'finally' block", ('<file>', 2, 9, '    pass\n', 2, -1))
