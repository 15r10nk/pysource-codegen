from ast import Constant
from ast import Expr
from ast import JoinedStr
from ast import Module

tree = Module(body=[Expr(value=JoinedStr(values=[Constant(value="'"), Constant(value="'")]))])

# version: 3.14.3
# seed = 9420455254
#
# tree.body[0].value.values: [0: Constant(value="''")] != [0: Constant(value="'"), 1: Constant(value="'")]
# Source:
# f"''"
#
# Adjacent Constant strings in JoinedStr.values are merged by ast.parse(ast.unparse(...)).
