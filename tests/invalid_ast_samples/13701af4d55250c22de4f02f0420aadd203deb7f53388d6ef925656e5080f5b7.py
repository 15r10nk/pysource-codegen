from ast import Constant
from ast import Expr
from ast import Module
from ast import TemplateStr

tree = Module(body=[Expr(value=TemplateStr(values=[Constant(value="")]))])

# version: 3.14.3
# seed = 3922679304
#
# tree.body[0].value.values: [] != [0: Constant(value='')]
# Source:
# t''
