from ast import Constant
from ast import Load
from ast import Match
from ast import match_case
from ast import MatchSequence
from ast import MatchValue
from ast import Module
from ast import Name
from ast import Pass

tree = Module(
    body=[
        Match(
            subject=Name(id="name_2", ctx=Load()),
            cases=[
                match_case(
                    pattern=MatchSequence(
                        patterns=[MatchValue(value=Constant(value=None))]
                    ),
                    body=[Pass()],
                )
            ],
        )
    ],
    type_ignores=[],
)

# version: 3.12.0
# seed = 4071349
#
# Source:
# match name_2:
#     case [None]:
#         pass
#
#
# Error:
#     ValueError('unexpected constant inside of a literal pattern')
