# pysource-codegen thinks that the this ast is valid python code, but this is not the case:
from ast import Constant
from ast import Expr
from ast import FormattedValue
from ast import JoinedStr
from ast import Module
tree = Module(body=[Expr(value=JoinedStr(values=[FormattedValue(value=JoinedStr(values=[]), conversion=-1, format_spec=None), Constant(value='\'\'\'"""}', kind=None)]))], type_ignores=[])

# version: 3.8.20
# seed = 5662766442
#
# Source:
#
# f'{f\'\'}\'\'\'"""}}'
#
#
