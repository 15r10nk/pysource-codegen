from ast import Constant
from ast import Global
from ast import Load
from ast import Match
from ast import match_case
from ast import MatchAs
from ast import MatchValue
from ast import Module
from ast import Name

tree = Module(
    body=[
        Match(
            subject=Name(id="name_3", ctx=Load()),
            cases=[
                match_case(
                    pattern=MatchAs(
                        pattern=MatchValue(value=Constant(value=0.0)), name="name_0"
                    ),
                    body=[Global(names=["name_0"])],
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
#     case 0.0 as name_0:
#         global name_0
#
#
# Error:
#     SyntaxError("name 'name_0' is assigned to before global declaration")
