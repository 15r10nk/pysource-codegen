from ast import BinOp
from ast import Load
from ast import Match
from ast import match_case
from ast import MatchValue
from ast import Module
from ast import Mult
from ast import Name
from ast import Pass
from ast import Store

tree = Module(
    body=[
        Match(
            subject=Name(id="name_1", ctx=Store()),
            cases=[
                match_case(
                    pattern=MatchValue(
                        value=BinOp(
                            left=Name(id="name_4", ctx=Load()),
                            op=Mult(),
                            right=Name(id="name_1", ctx=Load()),
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
#     case name_4 * name_1:
#         pass
#
#
# Error:
#     SyntaxError('invalid syntax', ('<file>', 2, 17, '    case name_4 * name_1:\n', 2, 18))
