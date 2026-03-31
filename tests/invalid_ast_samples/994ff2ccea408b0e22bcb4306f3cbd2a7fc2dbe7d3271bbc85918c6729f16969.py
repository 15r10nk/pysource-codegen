# pysource-codegen thinks that the this ast is valid python code, but this is not the case:
from ast import Constant
from ast import Expr
from ast import FormattedValue
from ast import JoinedStr
from ast import Load
from ast import Module
from ast import Name
tree = Module(body=[Expr(value=JoinedStr(values=[FormattedValue(value=Name(id='unique_name_0', ctx=Load()), conversion=115, format_spec=JoinedStr(values=[Constant(value="\\'", kind=None)]))]))], type_ignores=[])

# version: 3.8.20
# seed = 7310525802
#
# tree.body[0].value.values[0].format_spec.values[0].value: "'" != "\\'"Source:
#
# f"{unique_name_0!s:\'}"
#
#
