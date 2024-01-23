from ast import Constant
from ast import Load
from ast import Match
from ast import match_case
from ast import Module
from ast import Name
from ast import Pass

tree = Module(
    body=[
        Match(
            subject=Name(id="name_2", ctx=Load()),
            cases=[match_case(pattern=Constant(value=None), body=[Pass()])],
        )
    ],
    type_ignores=[],
)

# version: 3.12.0
# seed = 8897260
#
# Source:
# match name_2:
#     case None:
#         pass
#
#
# Error:
#     TypeError('expected some sort of pattern, but got <ast.Constant object at 0x7f91f9f81ed0>')
