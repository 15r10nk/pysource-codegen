from ast import Interpolation
from ast import parse
from ast import TemplateStr

tree = parse("t'{0 != 0:}'")
assert isinstance(tree.body[0].value, TemplateStr)
interpolation = tree.body[0].value.values[0]
assert isinstance(interpolation, Interpolation)
interpolation.str = "0 != 0"
