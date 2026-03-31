# pysource-codegen thinks that the this ast is valid python code, but this is not the case:
from ast import Constant
from ast import Expr
from ast import FormattedValue
from ast import JoinedStr
from ast import Module
tree = Module(body=[Expr(value=JoinedStr(values=[FormattedValue(value=Constant(value=b'', kind=None), conversion=115, format_spec=JoinedStr(values=[Constant(value='\'\'\'"""', kind=None)]))]))], type_ignores=[])

# version: 3.8.20
# seed = 5924944782
#
# Source:
#
# f'{b\'\'!s:\'\'\'"""}'
#
#
