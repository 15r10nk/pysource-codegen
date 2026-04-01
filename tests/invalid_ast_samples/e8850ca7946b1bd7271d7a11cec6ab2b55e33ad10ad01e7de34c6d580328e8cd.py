# pysource-codegen thinks that the this ast is valid python code, but this is not the case:
from ast import *
tree = Module(body=[Expr(value=JoinedStr(values=[FormattedValue(value=Constant(value='', kind=None), conversion=115, format_spec=None), Constant(value='"', kind=None)]))], type_ignores=[])

# version: 3.8.20
# seed = 3652823334
# 
# Source:
# 
# f"""{''!s}""""
# 
# 
