from ast import AnnAssign
from ast import Load
from ast import Module
from ast import Name
from ast import Store

assignment = AnnAssign.__new__(AnnAssign)
assignment.target = Name(id="x", ctx=Store())
assignment.annotation = Name(id="int", ctx=Load())
assignment.value = None
tree = Module(body=[assignment], type_ignores=[])
