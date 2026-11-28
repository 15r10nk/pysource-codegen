from ast import Call
from ast import Expr
from ast import keyword
from ast import Load
from ast import Module
from ast import Name

tree = Module(
    body=[Expr(value=Call(
        func=Name(id="f", ctx=Load()),
        args=[],
        keywords=[keyword(arg=None, value=Name(id="x", ctx=Load()))],
    ))],
    type_ignores=[],
)
