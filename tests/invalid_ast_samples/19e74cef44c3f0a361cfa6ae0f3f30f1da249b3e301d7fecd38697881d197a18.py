from ast import Load
from ast import parse
from ast import Starred

tree = parse("[x for x in xs]")
comp = tree.body[0].value
comp.elt = Starred(value=comp.elt, ctx=Load())
