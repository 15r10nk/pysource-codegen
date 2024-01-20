from ast import Load
from ast import Match
from ast import match_case
from ast import MatchAs
from ast import MatchSingleton
from ast import Module
from ast import Name
from ast import Pass

tree = Module(
    body=[
        Match(
            subject=Name(id="name_2", ctx=Load()),
            cases=[
                match_case(
                    pattern=MatchAs(
                        pattern=MatchAs(pattern=MatchSingleton(value=None)),
                        name="name_4",
                    ),
                    body=[Pass()],
                )
            ],
        )
    ],
    type_ignores=[],
)

# version: 3.12.0
# seed = 2121918
#
# Source:
# match name_2:
#     case _ as name_4:
#         pass
#
#
# Error:
#     ValueError('MatchAs must specify a target name if a pattern is given')
