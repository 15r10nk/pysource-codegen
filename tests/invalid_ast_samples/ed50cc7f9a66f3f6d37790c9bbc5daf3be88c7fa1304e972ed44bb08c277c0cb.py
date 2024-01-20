from ast import Constant
from ast import Load
from ast import Match
from ast import match_case
from ast import MatchAs
from ast import MatchValue
from ast import Module
from ast import Name
from ast import Pass
from ast import UnaryOp
from ast import USub

tree = Module(
    body=[
        Match(
            subject=Name(id="name_4", ctx=Load()),
            cases=[
                match_case(pattern=MatchAs(), body=[Pass()]),
                match_case(
                    pattern=MatchValue(
                        value=UnaryOp(op=USub(), operand=Constant(value=0))
                    ),
                    body=[Pass()],
                ),
            ],
        )
    ],
    type_ignores=[],
)

# version: 3.12.0
# seed = 7662891
#
# Source:
# match name_4:
#     case _:
#         pass
#     case -0:
#         pass
#
#
# Error:
#     SyntaxError('wildcard makes remaining patterns unreachable', ('<file>', 2, 10, None, 2, 11))
