from ast import Load
from ast import Match
from ast import match_case
from ast import MatchValue
from ast import Module
from ast import Name
from ast import Pass

tree = Module(
    body=[
        Match(
            subject=Name(id="name_3", ctx=Load()),
            cases=[
                match_case(
                    pattern=MatchValue(value=Name(id="name_4", ctx=Load())),
                    body=[Pass()],
                ),
                match_case(
                    pattern=MatchValue(value=Name(id="name_1", ctx=Load())),
                    body=[Pass()],
                ),
            ],
        )
    ],
    type_ignores=[],
)

# version: 3.12.0
#
# Source:
# match name_3:
#     case name_4:
#         pass
#     case name_1:
#         pass
#
#
# Error:
#     SyntaxError("name capture 'name_4' makes remaining patterns unreachable", ('<file>', 2, 10, None, 2, 16))
