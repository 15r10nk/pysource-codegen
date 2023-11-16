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
            subject=Name(id="name_1", ctx=Load()),
            cases=[
                match_case(
                    pattern=MatchValue(
                        value=UnaryOp(
                            op=USub(),
                            operand=UnaryOp(op=USub(), operand=Constant(value=0.0)),
                        )
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
# match name_1:
#     case --0.0:
#         pass
#
#
# Error:
#     SyntaxError('invalid syntax', ('<file>', 2, 11, '    case --0.0:\n', 2, 12))
