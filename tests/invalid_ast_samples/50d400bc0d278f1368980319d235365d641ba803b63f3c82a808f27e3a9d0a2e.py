from ast import Attribute
from ast import Constant
from ast import Load
from ast import Match
from ast import match_case
from ast import MatchClass
from ast import Module
from ast import Pass

tree = Module(
    body=[
        Match(
            subject=Constant(value=0),
            cases=[
                match_case(
                    pattern=MatchClass(
                        cls=Attribute(
                            value=Constant(value=0), attr="name_0", ctx=Load()
                        )
                    ),
                    body=[Pass()],
                )
            ],
        )
    ]
)

# version: 3.14.0
# seed = 4169242358
#
# Source:
# match 0:
#     case 0 .name_0():
#         pass
#
#
# Error:
#     SyntaxError('invalid syntax', ('<file>', 2, 12, '    case 0 .name_0():\n', 2, 13))
