from ast import Constant
from ast import Expr
from ast import Module
from ast import TemplateStr

tree = Module(body=[Expr(value=TemplateStr(values=[Constant(value="t", kind="some text")]))])

# version: 3.14.3
# seed = 8873225864
#
# tree.body[0].value.values[0].kind: None != 'some text'
# Source:
# t't'
