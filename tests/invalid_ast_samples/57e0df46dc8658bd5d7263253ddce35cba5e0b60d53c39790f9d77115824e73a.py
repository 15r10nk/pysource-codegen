# pysource-codegen thinks that the this ast is valid python code, but this is not the case:
from ast import *
tree = Module(body=[Expr(value=JoinedStr(values=[FormattedValue(value=Constant(value=b'\x00', kind=None), conversion=115, format_spec=None)]))], type_ignores=[])

# version: 3.8.20
# seed = 2136530776
# 
# Source:
# 
# f"{b'\x00'!s}"
# 
# 
