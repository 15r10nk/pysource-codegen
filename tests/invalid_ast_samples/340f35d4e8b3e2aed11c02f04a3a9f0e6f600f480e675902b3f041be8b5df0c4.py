from ast import Load
from ast import Match
from ast import match_case
from ast import MatchSingleton
from ast import Module
from ast import Name
from ast import Pass

tree = Module(
    body=[
        Match(
            subject=Name(id="name_2", ctx=Load()),
            cases=[
                match_case(pattern=MatchSingleton(value=b"some bytes"), body=[Pass()])
            ],
        )
    ],
    type_ignores=[],
)

# version: 3.12.0
# seed = 8718137
#
# Source:
# match name_2:
#     case b'some bytes':
#         pass
#
#
# Error:
#     ValueError('MatchSingleton can only contain True, False and None')
