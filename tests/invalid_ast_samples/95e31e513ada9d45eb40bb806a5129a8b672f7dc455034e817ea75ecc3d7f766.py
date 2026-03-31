# pysource-codegen thinks that the this ast is valid python code, but this is not the case:
from ast import *
tree = Module(body=[Expr(value=JoinedStr(values=[Constant(value="\\'\\", kind=None), FormattedValue(value=Name(id='unique_name_0', ctx=Load()), conversion=115, format_spec=None)]))], type_ignores=[])

# version: 3.8.20
# seed = 3792395058
# 
# tree.body[0].value.values[0].value: "'\\" != "\\'\\"Source:
# 
# f"\'\{unique_name_0!s}"
# 
# 
