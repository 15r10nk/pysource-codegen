from ast import Constant
from ast import Load
from ast import Match
from ast import match_case
from ast import MatchValue
from ast import Module
from ast import Name
from ast import Pass
from ast import UnaryOp
from ast import USub

tree = Module(
    body=[
        Match(
            subject=Name(id="name_3", ctx=Load()),
            cases=[
                match_case(
                    pattern=MatchValue(
                        value=UnaryOp(op=USub(), operand=Constant(value=False))
                    ),
                    body=[Pass()],
                )
            ],
        )
    ],
    type_ignores=[],
)

# version: 3.10.8
#
# Source:
# match name_3:
#     case -False:
#         pass
#
#
# Error:
#     SyntaxError('invalid syntax', ('<file>', 2, 11, '    case -False:\n', 2, 16))
