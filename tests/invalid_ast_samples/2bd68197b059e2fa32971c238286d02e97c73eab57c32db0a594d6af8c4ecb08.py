from ast import Module
from ast import Pass
from ast import Try

tree = Module(
    body=[Try(body=[Pass()], handlers=[], orelse=[], finalbody=[])], type_ignores=[]
)

# version: 3.9.15
# seed = 4634023
#
# Source:
# try:
#     pass
#
#
# Error:
#     SyntaxError('unexpected EOF while parsing', ('<file>', 2, 9, '    pass\n'))
