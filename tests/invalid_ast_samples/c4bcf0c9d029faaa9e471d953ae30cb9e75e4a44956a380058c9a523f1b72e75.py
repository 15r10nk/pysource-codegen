from ast import *

tree = Module(
    body=[
        Delete(targets=[Call(func=Name(id="name_5", ctx=Load()), args=[], keywords=[])])
    ],
    type_ignores=[],
)

# version: 3.12.0
#
# Source:
# del name_5()
#
#
# Error:
#     SyntaxError('cannot delete function call', ('<file>', 1, 5, 'del name_5()\n', 1, 13))
