from ast import Global
from ast import Load
from ast import Match
from ast import match_case
from ast import MatchSequence
from ast import MatchStar
from ast import Module
from ast import Name

tree = Module(
    body=[
        Match(
            subject=Name(id="name_0", ctx=Load()),
            cases=[
                match_case(
                    pattern=MatchSequence(patterns=[MatchStar(name="name_5")]),
                    body=[Global(names=["name_5"])],
                )
            ],
        )
    ]
)

# version: 3.13.0b1
# seed = 3678395
#
# Source:
# match name_0:
#     case [*name_5]:
#         global name_5
#
#
# Error:
#     SyntaxError("name 'name_5' is assigned to before global declaration")
